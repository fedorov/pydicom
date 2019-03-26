# Copyright 2008-2018 pydicom authors. See LICENSE file for details.
# -*- coding: utf-8 -*-
"""Access SR dictionary information"""

from itertools import chain
import inspect

from pydicom.sr._concepts_dict import concepts
from pydicom.sr._cid_dict import cid_concepts
from pydicom.sr.value_types import CodedConcept

def _filtered(allnames, filters):
    """Helper function for dir() methods"""
    matches = {}
    for filter_ in filters:
        filter_ = filter_.lower()
        match = [x for x in allnames if x.lower().find(filter_) != -1]
        matches.update(dict([(x, 1) for x in match]))
    if filters:
        names = sorted(matches.keys())
        return names
    else:
        return sorted(allnames)  


class _CID_Dict(object):
    def __init__(self, cid):
        self.cid = cid

    def __dir__(self):
        """Gives a list of available SR identifiers.

        List of attributes is used, for example, in auto-completion in editors
        or command-line environments.
        """
        # Force zip object into a list in case of python3. Also backwards
        # compatible
        meths = set(list(zip(
            *inspect.getmembers(self.__class__, inspect.isroutine)))[0])
        props = set(list(zip(
            *inspect.getmembers(self.__class__, inspect.isdatadescriptor)))[0])
        sr_names = set(self.dir())
        alldir = sorted(props | meths | sr_names)
        return alldir

    def __getattr__(self, name):
        matches = [scheme for scheme, keywords in cid_concepts[self.cid].items()
                    if name in keywords]
        if not matches:
            msg = "Identifier '{}' not found for cid{}".format(name, self.cid)
            raise AttributeError(msg)
        elif len(matches) > 1:
            # Should never happen, but just in case
            msg = "Multiple schemes found for '{}' in cid{}".format(name, cid)
            raise AssertionError(msg)       
        else:
            scheme = matches[0]
            concept = concepts[scheme][name]
            # Almost always only one code per concepts name
            if len(concept) == 1:
                code, val = list(concept.items())[0]
            else:
                matches = [(code, val) for code, val in concept.items()
                           if self.cid in val[1]]
                if len(matches) > 1:
                    # Should never happen, but check in case
                    msg = "{} had multiple code matches for cid{}".format(name, cid)
                    raise AssertionError(msg)
                code, val = matches[0]
            return CodedConcept(value=code,
                                meaning=val[0],
                                scheme_designator=scheme
                               )

        
    def dir(self, *filters):
        """Return an alphabetical list of SR identifiers based on a partial match.

        Intended mainly for use in interactive Python sessions. 

        Parameters
        ----------
        filters : str
            Zero or more string arguments to the function. Used for
            case-insensitive match to any part of the SR keyword.

        Returns
        -------
        list of str
            The matching SR keywords. If no filters are
            used then all keywords are returned.
        """
        allnames = set(chain(*cid_concepts[self.cid].values()))
        return _filtered(allnames, filters)

    def trait_names(self):
        """Return a list of valid names for auto-completion code.

        Used in IPython, so that data element names can be found and offered
        for autocompletion on the IPython command line.
        """
        return dir(self)

        
class _ConceptsDict(object):
    def __init__(self, scheme=None):
        self.scheme = scheme
        if scheme:
            self._dict = {scheme: concepts[scheme]}
        else:
            self._dict = concepts

    def __dir__(self):
        """Gives a list of available SR identifiers.

        List of attributes is used, for example, in auto-completion in editors
        or command-line environments.
        """
        # Force zip object into a list in case of python3. Also backwards
        # compatible
        meths = set(list(zip(
            *inspect.getmembers(self.__class__, inspect.isroutine)))[0])
        props = set(list(zip(
            *inspect.getmembers(self.__class__, inspect.isdatadescriptor)))[0])
        sr_names = set(self.dir())
        alldir = sorted(props | meths | sr_names)
        return alldir
        
    def __getattr__(self, name):
        if name.startswith("cid"):
            if not self.scheme:
                return _CID_Dict(int(name[3:]))
            raise AttributeError("Cannot call cid selector on scheme dict")
        if name in self._dict.keys():
            # Return concepts limited only the specified scheme designator
            return _ConceptsDict(scheme=name)
        # else try to find in any scheme
        if self.scheme:
            scheme = self.scheme
        else:
            matches = [scheme for scheme, codes in self._dict.items()
                       if name in codes]
            if len(matches) == 1:
                scheme = matches[0]
            else:
                msg = "Name '{}' is present in multiple schemes: {}"
                msg += "Please access through codes.<scheme or cid>.<name> format"
                raise KeyError(msg.format(name, matches))
        
        val = self._dict[scheme][name]
        # val is like {code1: (meaning, cid_list}, code2: ...}
        if len(val) > 1: # more than one code for this name 
            raise NotImplementedError("Need cid to disambiguate")
        else:
            code = list(val.keys())[0] # get first and only
            meaning, cids = val[code]
            return CodedConcept(value=code,
                                meaning=meaning,
                                scheme_designator=scheme
                               )

    def dir(self, *filters):
        """Return an alphabetical list of SR identifiers based on a partial match.

        Intended mainly for use in interactive Python sessions. 

        Parameters
        ----------
        filters : str
            Zero or more string arguments to the function. Used for
            case-insensitive match to any part of the SR keyword.

        Returns
        -------
        list of str
            The matching SR keywords. If no filters are
            used then all keywords are returned.
        """
        allnames = set(chain(*(x.keys() for x in self._dict.values())))
        return _filtered(allnames, filters)

    def schemes(self):
        return self._dict.keys()

    def trait_names(self):
        """Return a list of valid names for auto-completion code.

        Used in IPython, so that data element names can be found and offered
        for autocompletion on the IPython command line.
        """
        return dir(self)


codes = _ConceptsDict()

