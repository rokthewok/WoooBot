#! /usr/bin/python3
import discord
import random
import wbot_commands.command


class InvalidProductionError(Exception):
    pass


class DiceRoller(object):
    def __init__(self):
        pass

    def _parse(self, production):
        current_token = '';
        index = 0
        state = 'start'
        tokens = []
        while index < len(production):
            char = production[index]
            if char == ' ':
                # skip spaces
                index += 1
            elif state == 'start':
                # looking for a number here
                if char in '123456789':
                    state = 'number'
                else:
                    print('bad starting state; current character: {}'.format(char))
                    raise InvalidProductionError()
            elif state == 'number':
                if char in '123456789' and len(current_token) == 0 or \
                                        char in '0123456789' and len(current_token) > 0:
                    current_token += char
                    index += 1
                elif len(current_token) == 0:
                    print('bad number token; current character: {}'.format(char))
                    raise InvalidProductionError()
                elif char in '+-':
                    state = 'arithmetic'
                    tokens.append(('number', current_token))
                    current_token = ''
                elif char in 'd':
                    state = 'dice'
                    tokens.append(('number', current_token))
                    current_token = ''
                else:
                    print('bad number token; current character: {}'.format(char))
                    raise InvalidProductionError()
            elif state == 'arithmetic':
                if char in '+-' and len(current_token) == 0:
                    current_token += char
                    index += 1
                elif len(current_token) == 0:
                    print('bad arithmetic token; current character: {}'.format(char))
                    raise InvalidProductionError()
                elif char in '123456789':
                    state = 'number'
                    tokens.append(('operator', current_token))
                    current_token = ''
                else:
                    print('bad arithmetic token; current character: {}'.format(char))
                    raise InvalidProductionError()
            elif state == 'dice':
                if char in 'd' and len(current_token) == 0:
                    current_token += char
                    index += 1
                elif len(current_token) == 0:
                    print('bad dice token; current character: {}'.format(char))
                    raise InvalidProductionError()
                elif char in '123456789':
                    state = 'dice_number'
                    tokens.append(('operator', current_token))
                    current_token = ''
                else:
                    print('bad dice token; current character: {}'.format(char))
                    raise InvalidProductionError()
            elif state == 'dice_number':
                if char in '123456789' and len(current_token) == 0 or \
                                        char in '0123456789' and len(current_token) > 0:
                    current_token += char
                    index += 1
                elif len(current_token) == 0:
                    print('bad dice_number token; current character: {}'.format(char))
                    raise InvalidProductionError()
                elif char in '+-':
                    state = 'arithmetic'
                    tokens.append(('number', current_token))
                    current_token = ''
                else:
                    print('bad dice_number token; current character: {}'.format(char))
                    raise InvalidProductionError()
            else:
                print('unknown state; state: {}'.format(state))
                raise InvalidProductionError()

        if state != 'number' and state != 'dice_number':
            print('invalid final state; state: {}'.format(state))
            raise InvalidProductionError()

        # append the last token
        tokens.append(('number', current_token))

        return tokens

    def roll(self, production):
        tokens = self._parse(production)
        print(tokens)
        return self._do_math(tokens)

    def _do_math(self, tokens):
        # now we have our tokens; let's actually do something with them
        result = 0
        rpn_list = []
        operator_stack = []
        for token in tokens:
            if token[0] == 'number':
                rpn_list.append(int(token[1]))
            elif token[0] == 'operator':
                while len(operator_stack) > 0:
                    if (operator_stack[-1] in 'd' and token[1] in 'd') or \
                            (operator_stack[-1] in '+-d' and token[1] in '+-'):
                        rpn_list.append(operator_stack[-1])
                        operator_stack.pop()
                    else:
                        break
                operator_stack.append(token[1])
            else:
                raise InvalidProductionError()

        for op in operator_stack:
            rpn_list.append(op)

        print(rpn_list)
        result_stack = []
        for token in rpn_list:
            if isinstance(token, int):
                result_stack.append(token)
            elif isinstance(token, str):
                right_operand = result_stack[-1]
                result_stack.pop()
                left_operand = result_stack[-1]
                result_stack.pop()
                if token == '+':
                    result = left_operand + right_operand
                if token == '-':
                    result = left_operand - right_operand
                elif token == 'd':
                    result = left_operand * random.randint(1, right_operand)
                result_stack.append(result)
            else:
                raise InvalidProductionError()

        if len(result_stack) > 1:
            raise InvalidProductionError()
        # the only remaining value on the stack is our result
        return result_stack[0]


class RollCommand(wbot_commands.command.Command):
    """Command that rolls dice with the given productions:
        [1-9][0-9]*d(2|4|6|8|10|12|20|100]((\+|\-)[1-9][0-9]*)?
    """
    NAME = 'roll'

    def __init__(self):
        wbot_commands.command.Command.__init__(self,
                                               help={
                                                   'name': RollCommand.NAME,
                                                   'text': 'make dice rolls - <times>d<sides> +- <modifier>'
                                               })
        random.seed()

    def do(self, text):
        """Perform the action described by this command - roll dice for a given production.
        """
        print('Dice roll production: {}'.format(text))
        if not text:
            return None
        roller = DiceRoller()
        result = 0
        try:
            result = roller.roll(text)
            print('roll: {}'.format(result))
        except InvalidProductionError as e:
            print('bad roll production: {}'.format(text))
            return 'Sorry, "{}" is an invalid roll statement'.format(text)
        return 'You rolled: {}'.format(result)
