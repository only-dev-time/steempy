from unittest.mock import Mock

from steem.post import Post
from steem.utils import findall_patch_hunks


def test_post_refresh():
    """ Post should load correctly if passed a dict or string identifier. """
    p1 = Post('https://steemit.com/marketing/@steemitblog/'
              'marketing-w-mitchell-a-steem-ecosystem')
    p2 = Post({
        'author': 'steemitblog',
        'permlink': 'marketing-w-mitchell-a-steem-ecosystem'
    })

    # did post load?
    assert 'json_metadata' in p1 and 'json_metadata' in p2

    # are posts the same
    assert p1.export() == p2.export()


def test_post_edit_creates_patch():
    post = Post.__new__(Post)
    post.update({
        "author": "alice",
        "permlink": "original",
        "parent_author": "parent",
        "parent_permlink": "root",
        "title": "Title",
        "body": "old body",
        "json_metadata": {},
    })
    post.commit = Mock()

    post.edit("new body", meta={"app": "steempy"})

    post.commit.post.assert_called_once()
    args, kwargs = post.commit.post.call_args
    assert args[0] == "Title"
    assert args[1].startswith("@@")
    assert findall_patch_hunks(args[1]) == [("1", "7", "1", "7", "")]
    assert "old" in args[1]
    assert "new" in args[1]
    assert kwargs == {
        "author": "alice",
        "permlink": "original",
        "reply_identifier": "parent/root",
        "json_metadata": {"app": "steempy"},
    }


def test_post_edit_replace():
    post = Post.__new__(Post)
    post.update({
        "author": "alice",
        "permlink": "original",
        "parent_author": "parent",
        "parent_permlink": "root",
        "title": "Title",
        "body": "old body",
        "json_metadata": {},
    })
    post.commit = Mock()

    post.edit("new body", replace=True)

    post.commit.post.assert_called_once()
    args, kwargs = post.commit.post.call_args
    assert args == ("Title", "new body")
    assert kwargs == {
        "author": "alice",
        "permlink": "original",
        "reply_identifier": "parent/root",
        "json_metadata": {},
    }
