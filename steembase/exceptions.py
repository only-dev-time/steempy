import re


def decode_rpc_error_msg(e):
    """ Helper function to decode the raised Exception and give it a
        python Exception class
    """
    found = re.search(
        ("(10 assert_exception: Assert Exception\n|"
         "3030000 tx_missing_posting_auth)"
         ".*: (.*)\n"),
        str(e),
        flags=re.M)
    if found:
        return found.group(2).strip()
    else:
        return str(e)

def decodeRPCErrorMsg(e):  # noqa: N802
    """ **Deprecated. Use ``decode_rpc_error_msg`` instead.**

        Helper function to decode the raised Exception and give it a
        python Exception class
    """
    import warnings
    warnings.warn(
        "decodeRPCErrorMsg() is deprecated; use decode_rpc_error_msg() "
        "instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return decode_rpc_error_msg(e)

class RPCError(Exception):
    pass


class RPCErrorRecoverable(RPCError):  # noqa: N818
    pass


class NumRetriesReached(Exception):  # noqa: N818
    pass


class NoAccessApi(RPCError):  # noqa: N818
    pass


class AlreadyTransactedThisBlock(RPCError):  # noqa: N818
    pass


class VoteWeightTooSmall(RPCError):  # noqa: N818
    pass


class OnlyVoteOnceEvery3Seconds(RPCError):  # noqa: N818
    pass


class AlreadyVotedSimilarily(RPCError):  # noqa: N818
    pass


class NoMethodWithName(RPCError):  # noqa: N818
    pass


class PostOnlyEvery5Min(RPCError):  # noqa: N818
    pass


class DuplicateTransaction(RPCError):  # noqa: N818
    pass


class MissingRequiredPostingAuthority(RPCError):  # noqa: N818
    pass


class UnhandledRPCError(RPCError):
    pass


class ExceededAllowedBandwidth(RPCError):  # noqa: N818
    pass


class AccountExistsException(Exception):  # noqa: N818
    pass


class AccountDoesNotExistsException(Exception):  # noqa: N818
    pass


class InsufficientAuthorityError(Exception):
    pass


class MissingKeyError(Exception):
    pass


class BlockDoesNotExistsException(Exception):  # noqa: N818
    pass


class WitnessDoesNotExistsException(Exception):  # noqa: N818
    pass


class InvalidKeyFormat(Exception):  # noqa: N818
    pass


class NoWallet(Exception):  # noqa: N818
    pass


class InvalidWifError(Exception):
    pass


class WalletExists(Exception):  # noqa: N818
    pass


class PostDoesNotExist(Exception):  # noqa: N818
    pass


class VotingInvalidOnArchivedPost(Exception):  # noqa: N818
    pass


class SaltVerificationError(Exception):
    """ Raised when the salt verification fails. """
    pass


class WrongKEKError(Exception):
    """ Raised when the KEK is wrong. """
    pass
