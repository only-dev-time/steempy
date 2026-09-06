import logging
import os
import warnings

from steembase import bip38
from steembase.account import PrivateKey
from steembase.exceptions import InvalidWifError
from steembase.exceptions import WalletExists

from .account import Account
from .instance import shared_steemd_instance


log = logging.getLogger(__name__)


class Wallet:
    """ The wallet is meant to maintain access to private keys for
        your accounts. It either uses manually provided private keys
        or uses a SQLite database managed by storage.py.

        :param Steem rpc: RPC connection to a Steem node

        :param array,dict,string keys: Predefine the wif keys to shortcut
        the wallet database

        Three wallet operation modes are possible:

        * **Wallet Database**: Here, steemlibs loads the keys from the
          locally stored wallet SQLite database (see ``storage.py``).
          To use this mode, simply call ``Steem()`` without the
          ``keys`` parameter
        * **Providing Keys**: Here, you can provide the keys for
          your accounts manually. All you need to do is add the wif
          keys for the accounts you want to use as a simple array
          using the ``keys`` parameter to ``Steem()``.
        * **Force keys**: This more is for advanced users and
          requires that you know what you are doing. Here, the
          ``keys`` parameter is a dictionary that overwrite the
          ``active``, ``owner``, ``posting`` or ``memo`` keys for
          any account. This mode is only used for *foreign*
          signatures!
    """
    decrypted_kek = None

    # Keys from database
    config_storage = None
    key_encryption_key = None
    key_storage = None

    # Manually provided keys
    keys = {}  # struct with pubkey as key and wif as value
    key_map = {}  # type:wif pairs to force certain keys

    def __init__(self, steemd_instance=None, **kwargs):
        from steembase.storage import config_storage
        self.config_storage = config_storage

        # RPC
        self.steemd = steemd_instance or shared_steemd_instance()

        # Prefix
        if self.steemd:
            self.prefix = self.steemd.chain_params["prefix"]
        else:
            # If not connected, load prefix from config
            self.prefix = self.config_storage["prefix"]

        if "keys" in kwargs:
            self.set_keys(kwargs["keys"])
        else:
            """ If no keys are provided manually we load the SQLite
                keyStorage
            """
            from steembase.storage import KeyEncryptionKey
            from steembase.storage import key_storage
            self.key_encryption_key = KeyEncryptionKey
            self.key_storage = key_storage

    def set_keys(self, loadkeys):
        """ This method is strictly only for in memory keys that are
            passed to Wallet/Steem with the ``keys`` argument
        """
        log.debug(
            "Force setting of private keys. Not using the wallet database!")
        if isinstance(loadkeys, dict):
            Wallet.key_map = loadkeys
            loadkeys = list(loadkeys.values())
        elif not isinstance(loadkeys, list):
            loadkeys = [loadkeys]

        for wif in loadkeys:
            try:
                key = PrivateKey(wif)
            except:  # noqa FIXME(sneak)
                raise InvalidWifError from None
            Wallet.keys[format(key.pubkey, self.prefix)] = str(key)

    def unlock(self, user_passphrase=None):
        """ Unlock the wallet database
        """
        if not self.created():
            self.new_wallet()

        if (self.decrypted_kek is None
                and self.config_storage[self.key_encryption_key.config_key]):
            if user_passphrase is None:
                user_passphrase = self.get_user_passphrase()
            kek = self.key_encryption_key(user_passphrase)
            self.decrypted_kek = kek.decrypted_kek

    def lock(self):
        """ Lock the wallet database
        """
        self.decrypted_kek = None

    def locked(self):
        """ Is the wallet database locked?
        """
        return False if self.decrypted_kek else True

    def change_user_passphrase(self):
        """ Change the user entered password for the wallet database
        """
        # Open Existing Wallet
        pwd = self.get_user_passphrase()
        kek = self.key_encryption_key(pwd)
        self.decrypted_kek = kek.decrypted_kek
        # Provide new passphrase
        print("Please provide the new passphrase")
        newpwd = self.get_user_passphrase(confirm=True)
        # Change passphrase
        kek.change_passphrase(newpwd)

    def created(self):
        """ Do we have a wallet database already?
        """
        if len(self.get_public_keys()):
            # Already keys installed
            return True
        elif self.key_encryption_key.config_key in self.config_storage:
            # no keys but a KeyEncryptionKey
            return True
        else:
            return False

    def new_wallet(self):
        """ Create a new wallet database
        """
        if self.created():
            raise WalletExists("You already have created a wallet!")
        print("Please provide a passphrase for the new wallet")
        pwd = self.get_user_passphrase(confirm=True)
        kek = self.key_encryption_key(pwd)
        self.decrypted_kek = kek.decrypted_kek

    def encrypt_wif(self, wif):
        """ Encrypt a wif key
        """
        self.unlock()
        return format(
            bip38.encrypt(PrivateKey(wif), self.decrypted_kek), "encwif")

    def decrypt_wif(self, encwif):
        """ decrypt a wif key
        """
        try:
            # Try to decode as wif
            PrivateKey(encwif)
            return encwif
        except:  # noqa FIXME(sneak)
            pass
        self.unlock()
        return format(bip38.decrypt(encwif, self.decrypted_kek), "wif")

    def get_user_passphrase(self, confirm=False, text='Passphrase: '):
        """ Obtain a passphrase from the user
        """
        import getpass
        if "UNLOCK" in os.environ:
            # overwrite passphrase from environmental variable
            return os.environ.get("UNLOCK")
        if confirm:
            # Loop until both match
            while True:
                pw = self.get_user_passphrase(confirm=False)
                if not pw:
                    print("You cannot choose an empty password! " +
                          "If you want to automate the use of the library, " +
                          "please use the `UNLOCK` environmental variable!")
                    continue
                else:
                    pwck = self.get_user_passphrase(
                        confirm=False, text="Confirm Passphrase: ")
                    if pw == pwck:
                        return pw
                    else:
                        print("Given Passphrases do not match!")
        else:
            # return just one password
            return getpass.getpass(text)

    def add_private_key(self, wif):
        """ Add a private key to the wallet database
        """

        # it could be either graphenebase or pistonbase so we can't check
        # the type directly

        if isinstance(wif, PrivateKey) or isinstance(wif, PrivateKey):
            wif = str(wif)
        try:
            pub = format(PrivateKey(wif).pubkey, self.prefix)
        except:  # noqa FIXME(sneak)
            raise InvalidWifError(
                "Invalid Private Key Format. Please use WIF!") from None

        if self.key_storage:
            # Test if wallet exists
            if not self.created():
                self.new_wallet()
            self.key_storage.add(self.encrypt_wif(wif), pub)

    def get_private_key_for_public_key(self, pub):
        """ Obtain the private key for a given public key

            :param str pub: Public Key
        """
        if Wallet.keys:
            if pub in Wallet.keys:
                return Wallet.keys[pub]
            elif len(Wallet.keys) == 1:
                # If there is only one key in my overwrite-storage, then
                # use that one! Whether it will has sufficient
                # authorization is left to ensure by the developer
                return list(self.keys.values())[0]
        else:
            # Test if wallet exists
            if not self.created():
                self.new_wallet()

            return self.decrypt_wif(
                self.key_storage.get_private_key_for_public_key(pub))

    def remove_private_key_from_public_key(self, pub):
        """ Remove a key from the wallet database
        """
        if self.key_storage:
            # Test if wallet exists
            if not self.created():
                self.new_wallet()
            self.key_storage.delete(pub)

    def remove_account(self, account):
        """ Remove all keys associated with a given account
        """
        accounts = self.get_accounts()
        for a in accounts:
            if a["name"] == account:
                self.remove_private_key_from_public_key(a["pubkey"])

    def get_owner_key_for_account(self, name):
        """ Obtain owner Private Key for an account from the wallet database
        """
        if "owner" in Wallet.key_map:
            return Wallet.key_map.get("owner")
        else:
            account = self.steemd.get_account(name)
            if not account:
                return
            for authority in account["owner"]["key_auths"]:
                key = self.get_private_key_for_public_key(authority[0])
                if key:
                    return key
            return False

    def get_posting_key_for_account(self, name):
        """ Obtain owner Posting Key for an account from the wallet database
        """
        if "posting" in Wallet.key_map:
            return Wallet.key_map.get("posting")
        else:
            account = self.steemd.get_account(name)
            if not account:
                return
            for authority in account["posting"]["key_auths"]:
                key = self.get_private_key_for_public_key(authority[0])
                if key:
                    return key
            return False

    def get_memo_key_for_account(self, name):
        """ Obtain owner Memo Key for an account from the wallet database
        """
        if "memo" in Wallet.key_map:
            return Wallet.key_map.get("memo")
        else:
            account = self.steemd.get_account(name)
            if not account:
                return
            key = self.get_private_key_for_public_key(account["memo_key"])
            if key:
                return key
            return False

    def get_active_key_for_account(self, name):
        """ Obtain owner Active Key for an account from the wallet database
        """
        if "active" in Wallet.key_map:
            return Wallet.key_map.get("active")
        else:
            account = self.steemd.get_account(name)
            if not account:
                return
            for authority in account["active"]["key_auths"]:
                key = self.get_private_key_for_public_key(authority[0])
                if key:
                    return key
            return False

    def get_account_from_private_key(self, wif):
        """ Obtain account name from private key
        """
        pub = format(PrivateKey(wif).pubkey, self.prefix)
        return self.get_account_from_public_key(pub)

    def get_account_from_public_key(self, pub):
        """ Obtain account name from public key
        """
        # FIXME, this only returns the first associated key.
        # If the key is used by multiple accounts, this
        # will surely lead to undesired behavior
        names = self.steemd.call(
            'get_key_references', [pub], api="account_by_key_api")[0]
        if not names:
            return None
        else:
            return names[0]

    def get_account(self, pub):
        """ Get the account data for a public key
        """
        name = self.get_account_from_public_key(pub)
        if not name:
            return {"name": None, "type": None, "pubkey": pub}
        else:
            try:
                account = Account(name)
            except:  # noqa FIXME(sneak)
                return
            key_type = self.get_key_type(account, pub)
            return {
                "name": name,
                "account": account,
                "type": key_type,
                "pubkey": pub
            }

    def get_key_type(self, account, pub):
        """ Get key type
        """
        for authority in ["owner", "posting", "active"]:
            for key in account[authority]["key_auths"]:
                if pub == key[0]:
                    return authority
        if pub == account["memo_key"]:
            return "memo"
        return None

    def get_accounts(self):
        """ Return all accounts installed in the wallet database
        """
        pubkeys = self.get_public_keys()
        accounts = [self.get_account(pubkey) for pubkey in pubkeys if pubkey[:len(self.prefix)] == self.prefix]
        return accounts

    def get_accounts_with_permissions(self):
        """ Return a dictionary for all installed accounts with their
            corresponding installed permissions
        """
        accounts = [self.get_account(a) for a in self.get_public_keys()]
        r = {}
        for account in accounts:
            name = account["name"]
            if not name:
                continue
            permission_type = account["type"]
            if name not in r:
                r[name] = {
                    "posting": False,
                    "owner": False,
                    "active": False,
                    "memo": False
                }
            r[name][permission_type] = True
        return r

    def get_public_keys(self):
        """ Return all installed public keys
        """
        if self.key_storage:
            return self.key_storage.get_public_keys()
        else:
            return list(Wallet.keys.keys())

    def setKeys(self, loadkeys):  # noqa: N802
        """ **Deprecated. Use ``set_keys()`` instead.**

            This method is strictly only for in memory keys that are
            passed to Wallet/Steem with the ``keys`` argument
        """
        warnings.warn(
            "setKeys() is deprecated. Use set_keys() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.set_keys(loadkeys)

    def changeUserPassphrase(self):  # noqa: N802
        """ **Deprecated. Use ``set_keys()`` instead.**

            Change the user entered password for the wallet database
        """
        warnings.warn(
            "changeUserPassphrase() is deprecated; use "
            "change_user_passphrase() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.change_user_passphrase()

    def newWallet(self):  # noqa: N802
        """ **Deprecated. Use ``new_wallet()`` instead.**

            Create a new wallet database
        """
        warnings.warn(
            "newWallet() is deprecated; use new_wallet() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.new_wallet()

    def getUserPassphrase(self, confirm=False, text='Passphrase: '):  # noqa: N802
        """ **Deprecated. Use ``get_user_passphrase()`` instead.**

            Obtain a passphrase from the user
        """
        warnings.warn(
            "getUserPassphrase() is deprecated; use get_user_passphrase() "
            "instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_user_passphrase(confirm, text)

    def addPrivateKey(self, wif):  # noqa: N802
        """ **Deprecated. Use ``add_private_key()`` instead.**

            Add a private key to the wallet database
        """
        warnings.warn(
            "addPrivateKey() is deprecated; use add_private_key() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.add_private_key(wif)

    def getPrivateKeyForPublicKey(self, pub):  # noqa: N802
        warnings.warn(
            "getPrivateKeyForPublicKey() is deprecated; use "
            "get_private_key_for_public_key() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_private_key_for_public_key(pub)

    def removePrivateKeyFromPublicKey(self, pub):  # noqa: N802
        warnings.warn(
            "removePrivateKeyFromPublicKey() is deprecated; use "
            "remove_private_key_from_public_key() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.remove_private_key_from_public_key(pub)

    def removeAccount(self, account):  # noqa: N802
        warnings.warn(
            "removeAccount() is deprecated; use remove_account() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.remove_account(account)

    def getOwnerKeyForAccount(self, name):  # noqa: N802
        warnings.warn(
            "getOwnerKeyForAccount() is deprecated; use "
            "get_owner_key_for_account() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_owner_key_for_account(name)

    def getPostingKeyForAccount(self, name):  # noqa: N802
        warnings.warn(
            "getPostingKeyForAccount() is deprecated; use "
            "get_posting_key_for_account() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_posting_key_for_account(name)

    def getMemoKeyForAccount(self, name):  # noqa: N802
        warnings.warn(
            "getMemoKeyForAccount() is deprecated; use "
            "get_memo_key_for_account() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_memo_key_for_account(name)

    def getActiveKeyForAccount(self, name):  # noqa: N802
        warnings.warn(
            "getActiveKeyForAccount() is deprecated; use "
            "get_active_key_for_account() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_active_key_for_account(name)

    def getAccountFromPrivateKey(self, wif):  # noqa: N802
        warnings.warn(
            "getAccountFromPrivateKey() is deprecated; use "
            "get_account_from_private_key() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_account_from_private_key(wif)

    def getAccountFromPublicKey(self, pub):  # noqa: N802
        warnings.warn(
            "getAccountFromPublicKey() is deprecated; use "
            "get_account_from_public_key() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_account_from_public_key(pub)

    def getAccount(self, pub):  # noqa: N802
        warnings.warn(
            "getAccount() is deprecated; use get_account() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_account(pub)

    def getKeyType(self, account, pub):  # noqa: N802
        warnings.warn(
            "getKeyType() is deprecated; use get_key_type() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_key_type(account, pub)

    def getAccounts(self):  # noqa: N802
        warnings.warn(
            "getAccounts() is deprecated; use get_accounts() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_accounts()

    def getAccountsWithPermissions(self):  # noqa: N802
        warnings.warn(
            "getAccountsWithPermissions() is deprecated; use "
            "get_accounts_with_permissions() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_accounts_with_permissions()

    def getPublicKeys(self):  # noqa: N802
        warnings.warn(
            "getPublicKeys() is deprecated; use get_public_keys() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_public_keys()
