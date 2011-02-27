""" kinbaku.comments
"""

from kinbaku.comments.plugin import CommentsExtractor

plugin = CommentsExtractor

if __name__=='__main__':
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
