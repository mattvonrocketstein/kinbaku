""" kinbaku.comments
"""

from kinbaku.comments.plugin import CommentsExtractor
from kinbaku.comments.tools import extract_docstrings,extract_comments
plugin = CommentsExtractor

if __name__=='__main__':
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
