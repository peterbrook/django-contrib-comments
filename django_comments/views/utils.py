"""
A few bits of helper functions for comment views.
"""

import textwrap
try:
    from urllib.parse import urlencode
except ImportError:     # Python 2
    from urllib import urlencode

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
try:
    from django.shortcuts import resolve_url
except:
    from django.core import urlresolvers
    def resolve_url(to, *args, **kwargs):
        """
        Return a URL appropriate for the arguments passed.

        The arguments could be:

            * A model: the model's `get_absolute_url()` function will be called.

            * A view name, possibly with arguments: `urlresolvers.reverse()` will
              be used to reverse-resolve the name.

            * A URL, which will be returned as-is.

        """
        # If it's a model, use get_absolute_url()
        if hasattr(to, 'get_absolute_url'):
            return to.get_absolute_url()

        # Next try a reverse URL resolution.
        try:
            return urlresolvers.reverse(to, args=args, kwargs=kwargs)
        except urlresolvers.NoReverseMatch:
            # If this is a callable, re-raise.
            if callable(to):
                raise
            # If this doesn't "feel" like a URL, re-raise.
            if '/' not in to and '.' not in to:
                raise

        # Finally, fall back and assume it's a URL
        return to
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import is_safe_url

import django_comments

def next_redirect(request, fallback, **get_kwargs):
    """
    Handle the "where should I go next?" part of comment views.

    The next value could be a
    ``?next=...`` GET arg or the URL of a given view (``fallback``). See
    the view modules for examples.

    Returns an ``HttpResponseRedirect``.
    """
    next = request.POST.get('next')
    if not is_safe_url(url=next, host=request.get_host()):
        next = resolve_url(fallback)

    if get_kwargs:
        if '#' in next:
            tmp = next.rsplit('#', 1)
            next = tmp[0]
            anchor = '#' + tmp[1]
        else:
            anchor = ''

        joiner = ('?' in next) and '&' or '?'
        next += joiner + urlencode(get_kwargs) + anchor
    return HttpResponseRedirect(next)

def confirmation_view(template, doc="Display a confirmation view."):
    """
    Confirmation view generator for the "comment was
    posted/flagged/deleted/approved" views.
    """
    def confirmed(request):
        comment = None
        if 'c' in request.GET:
            try:
                comment = django_comments.get_model().objects.get(pk=request.GET['c'])
            except (ObjectDoesNotExist, ValueError):
                pass
        return render_to_response(template,
            {'comment': comment},
            context_instance=RequestContext(request)
        )

    confirmed.__doc__ = textwrap.dedent("""\
        %s

        Templates: :template:`%s``
        Context:
            comment
                The posted comment
        """ % (doc, template)
    )
    return confirmed
