

import lx
from . import const as c
from .const import NameToken as n
from .core import service as service


class NameOperator(object):

    def renderName(self, components):
        """ Renders name from given name components.
        
        Parameters
        ----------
        components : dict
            Dictionary of NameComponent/string value pairs.
        """
        nameFormat = self._nameScheme.formatGeneric
            
        nameFormatByType = self._nameScheme.formatByItemType
        if nameFormatByType:
            try:
                nameFormat = nameFormatByType[components[n.ITEM_TYPE]]
            except KeyError:
                pass

        return self._renderName(nameFormat, components)

    def renderNameMeta(self, components):
        """ Renders name for meta rig item from given components.
        """
        nameFormat = self._nameScheme.formatGenericMeta
            
        nameFormatByType = self._nameScheme.formatByGroupTypeMeta
        if nameFormatByType:
            try:
                nameFormat = nameFormatByType[components[n.ITEM_TYPE]]
            except KeyError:
                pass

        return self._renderName(nameFormat, components)

    def _renderName(self, nameFormat, components):
        """ Renders full item name using given naming format and name components.
        """
        itemTypes = self._nameScheme.itemTypeTokens

        name = ''
        nameComponents = [n.RIG_NAME,
                          n.MODULE_NAME,
                          n.BASE_NAME,
                          n.ITEM_TYPE,
                          n.ITEM_FEATURE,
                          n.MODO_ITEM_TYPE,
                          n.SIDE]

        side = {c.Side.CENTER: self._nameScheme.centerToken,
                c.Side.LEFT: self._nameScheme.leftToken,
                c.Side.RIGHT: self._nameScheme.rightToken}

        currentTokenResolved = False
        for token in nameFormat:
            previousTokenResolved = currentTokenResolved
            currentTokenResolved = False

            if token == n.ITEM_TYPE:
                try:
                    itemType = components[n.ITEM_TYPE]
                except KeyError:
                    continue

                # resolve type ident with the types.
                try:
                    resolvedPart = self._nameScheme.itemTypeTokens[itemType]
                except KeyError:
                    continue

            elif token == n.MODO_ITEM_TYPE:
                try:
                    modoItemType = components[n.MODO_ITEM_TYPE]
                except KeyError:
                    continue

                try:
                    resolvedPart = self._nameScheme.modoItemTypeTokens[modoItemType]
                except KeyError:
                    continue

            elif token == n.ITEM_FEATURE:
                allFeatures = ''

                try:
                    featureIdents = components[n.ITEM_FEATURE]
                except KeyError:
                    resolvedPart = None
                else:
                    for featureIdent in featureIdents:
                        try:
                            resolvedPart = self._nameScheme.itemFeatureTokens[featureIdent]
                        except KeyError:
                            resolvedPart = None
                        if resolvedPart is not None:
                            allFeatures += resolvedPart
                    resolvedPart = allFeatures

            elif token == n.SIDE:
                try:
                    resolvedPart = side[components[n.SIDE]]
                except KeyError:
                    continue

            # This is for tokens that do not require any extra processing.
            # Note that if that token is not present in components it's
            # simply skipped when the name is rendered.
            elif token in nameComponents:
                try:
                    resolvedPart = components[token]
                except KeyError:
                    continue

            else:
                # This for literal string
                resolvedPart = token
     
            if resolvedPart:
                # If the string starts with '<' it means that it depends
                # on previous token. Previous token needs to be successfully resolved
                # for the dependent one to be added to the name.
                if resolvedPart.startswith('<'):
                    if previousTokenResolved:
                        resolvedPart = resolvedPart[1:]
                    else:
                        continue
                name += resolvedPart
                currentTokenResolved = True

        return name
        
    def __init__(self, nameSchemeObject):
        self._nameScheme = nameSchemeObject