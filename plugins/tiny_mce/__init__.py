from ferris.core.plugins import register

register('tiny_mce')

from .component import TinyMce

__all__ = ['TinyMce']
