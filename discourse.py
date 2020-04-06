#!/usr/bin/python3

import json

# with open("pronouns.json") as jfile:
# 	PRONOUNS = json.loads(jfile.read())

# Begin discourse utility functions


def pronoun_flip(pronoun):
    pass


# End discourse utility functions


class ConversationStateHandler:
    '''attr: contexts keeps track of active 
    contexts, with their persistence
    counts as values, which decrements
    by one in each conversation step.
    Those that reach zero are eliminated from the
    next context'''

    def __init__(self):
        self.contexts = {'INIT': 1}
        self._context_vars = {'INIT': []}
        self.prior_intent = 'INIT'

    def step(self, step_dat):
        # provides count of how long the contexts are lasting
        self.contexts = {k: self.contexts[k] - 1 for k in self.contexts}
        self.contexts = {k: self.contexts[k] for k in self.contexts
                         if self.contexts[k] > 0}
        self._context_vars = {k: self._context_vars[k] for k in self.contexts}
        self.contexts.update(step_dat['counter'])
        self._context_vars.update(step_dat['vars'])
