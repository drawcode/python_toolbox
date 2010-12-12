# Copyright 2009-2010 Ram Rachum.
# This program is distributed under the LGPL2.1 license.

'''
This module defines the StepProfile class.

See its documentation for more information.
'''

import copy

from garlicsim.general_misc import caching
from garlicsim.general_misc import cute_inspect
from garlicsim.general_misc.arguments_profile import ArgumentsProfile
from garlicsim.general_misc import address_tools
from garlicsim.misc.exceptions import GarlicSimException

from garlicsim.misc.simpack_grokker.get_step_type import get_step_type


__all__ = ['StepProfile']


class StatePlaceholder(object): # blocktododoc: make uninstanciable
    # blocktododoc: bad name, it can also be a history browser
    pass


class StepProfile(ArgumentsProfile):
    '''
    Profile for doing simulation step, specifying step function and arguments.
    
    Using different step profiles, you can crunch your simulation in different
    ways, using different world laws, different contsants and different
    algorithm, within the same project.

    The step profile contains three things:
    
      1. A reference to the step fucntion.
      2. A list of arguments.
      3. A dict of keyword arguments
      
    For example, if you're doing a simulation of Newtonian Mechanics, you can
    create a step profile with `kwargs` of {'G': 3.0} in order to change the
    graviational constant of the simulation on-the-fly.
    '''
    # todo: perhaps this should be based on an ArgumentsProfile after all?
    # In __repr__ and stuff we'll just check self's class. How does Python
    # do it when you subclass its builtin types?

    
    __metaclass__ = caching.CachedType
    
    
    def __init__(self, step_function, *args, **kwargs):
        
        # Perhaps we were passed a StepProfile object instead of args
        # and kwargs? If so load that one, cause we're all cool and nice.
        candidate = None
        if len(args) == 1 and len(kwargs) == 0:
            candidate = args[0]
        if len(args) == 0 and len(kwargs) == 1 and \
           ('step_profile' in kwargs):
            candidate = kwargs['step_profile']
        
        if isinstance(candidate, StepProfile):
            ArgumentsProfile.__init__(self, candidate.step_function,
                                      *((StatePlaceholder,) + candidate.args),
                                      **candidate.kwargs)
        else:
            ArgumentsProfile.__init__(self, step_function,
                                      *((StatePlaceholder,) + args),
                                      **kwargs)

        assert self.args[0] is StatePlaceholder
        self.args = self.args[1:]
        
        self.step_function = self.function
        
    
    @caching.cache()    
    @staticmethod
    def build_parser(default_step_function):
        '''
        tododoc Create step profile, allowing the user to not specify step function.
        
        Most of the time when simulating, there is one default step function
        that should be used if no other step function was explicitly specified.
        But then again, we also want to allow the user to specify a step
        function if he desires. So we get the (*args, **kwargs) pair from the
        user, and we need to guess whether the user passed in a step function
        for to use, or didn't, and if he didn't we'll use the default one.
        
        The user may put the step function as the first positional argument, or
        as the 'step_function' keyword argument. 
        '''
        # blocktododoc: it's confusing thinking who should give the
        # `default_step_function`. make this clear in docstring, or possibly
        # make a function that returns a function.
        
        # blocktododoc: test it works with default_step_function=None, assuming
        # some step function is given, possibly in a step profile

        def parse_arguments_to_step_profile(*args, **kwargs):
        
            # We have two candidates to check now: args[0] and
            # kwargs['step_function']. We'll check the kwargs one first, because
            # that's more explicit and there's less chance we'll be catching
            # some other object by mistake.
            #
            # So we start with kwargs:
            
            if 'step_function' in kwargs:
                kwargs_copy = kwargs.copy()
                step_function = kwargs_copy.pop('step_function')
                
                get_step_type(step_function)
                # Just so things will break if it's not a step function. If the
                # user specified 'step_function', he's not going to get away
                # with it not being an actual step function.
    
                return StepProfile(step_function, *args, **kwargs_copy)
            
            
            if 'step_profile' in kwargs: # blocktododoc
                kwargs_copy = kwargs.copy()
                step_profile = kwargs_copy.pop('step_profile')
                
                if step_profile is None:
                    # We let the user specify `step_profile=None` if he wants to
                    # get the default step profile.
                    return StepProfile(default_step_function)
                    
                else: # step_profile is not None
                    if not isinstance(step_profile, StepProfile):
                        raise GarlicSimException(
                            "You passed in %s as a keyword argument with a "
                            "keyword of `step_profile`, but it's not a step "
                            "profile." % step_profile
                        )
                    return step_profile
    
            
            # No step function in kwargs. We'll try args:
            
            elif args:
                
                candidate = args[0]
                
                if isinstance(candidate, StepProfile):
                    return candidate
                
                try:
                    get_step_type(candidate)
                except Exception:
                    return StepProfile(
                        default_step_function,
                        *args,
                        **kwargs
                    )
                else:
                    args_copy = args[1:]
                    return StepProfile(
                        default_step_function,
                        *args_copy,
                        **kwargs
                    )
            
            else:
                return StepProfile(default_step_function, *args, **kwargs)
        
        return parse_arguments_to_step_profile
                
    
    def __repr__(self, short_form=False, root=None, namespace={}):
        '''
        Get a string representation of the step profile.
        
        Example output:
        StepProfile(<unbound method State.step>, 'billinear', t=7)
        '''
        
        if short_form:            
            describe = lambda thing: address_tools.describe(
                thing,
                shorten=True,
                root=root,
                namespace=namespace
            )
        else: # not short_form
            describe = repr

        args_string = ', '.join((describe(thing) for thing in self.args))
        kwargs_string = ', '.join(
            ('='.join((str(key), describe(value))) for
            (key, value) in self.kwargs.iteritems())
        )
        strings = filter(None, (args_string, kwargs_string))
        big_string = ', '.join(strings)
        
            
        if short_form:
            step_function_address = describe(self.step_function)
            final_big_string = ', '.join(
                filter(
                    None,
                    (
                        '<state>',
                        big_string
                    )
                )
            )
            return '%s(%s)' % (
                step_function_address,
                final_big_string
            )
            
        else:
            final_big_string = ', '.join(
                filter(
                    None,
                    (
                        describe(self.step_function),
                        big_string
                    )
                )
            )
            return '%s(%s)' % (type(self).__name__, final_big_string)
    

    @classmethod
    def create_from_dld_format(cls, step_function, args_dict, star_args_list,
                               star_kwargs_dict):
        args_spec = cute_inspect.getargspec(step_function)
        new_args = [args_dict[name] for name in args_spec.args[1:]] + \
                   list(star_args_list)
        return cls(step_function, *new_args, **star_kwargs_dict)
        
    
    def __eq__(self, other):
        return isinstance(other, StepProfile) and \
               ArgumentsProfile.__eq__(self, other)

    
    def __ne__(self, other):
        return not self.__eq__(other)