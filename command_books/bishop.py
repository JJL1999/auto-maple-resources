"""A collection of all commands that a Kanna can use to interact with the game."""

import math
import time

from src.common import config, settings, utils
from src.common.vkeys import press, key_down, key_up
from src.routine.components import Command


# List of key mappings
class Key:
    # Movement
    JUMP = 'space'
    TELEPORT = 'f'

    # Skills
    BIG_BANG = 's'
    PEACEMAKER = 'd'
    GENESIS = 'g'
    FOUNTAIN_OF_VENGEANCE = 'w'
    HOLY_ADVENT = 'f4'
    INFINITY = 'f5'
    UNRELIABLE_MEMORY = 'f6'
    ANGEL_OF_BALANCE = 'f1'
    BENEDICTION = 'f2'
    HEAVENS_DOOR = '`'

    # Commons
    ROPE_LIFT = 'c'
    ERDA_SHOWER = 't'
    SOL_JANUS = 'i'
    TERMS_AND_CONDITIONS = '3'


#########################
#       Commands        #
#########################
teleport_distance = settings.move_tolerance
horizon_teleport_distance = 0.5 * teleport_distance
jump_and_teleport_distance = 2 * settings.move_tolerance


def up(dy):
    if abs(dy) > jump_and_teleport_distance:
        jump = 'True' if abs(dy) > 1.6 * settings.move_tolerance else 'False'
        print(f"dy={dy}, 1.6*move_tolerance={1.6 * settings.move_tolerance}, jump={jump}")
        RopeLift(jump=jump).main()
    elif abs(dy) > teleport_distance:
        teleport('up', jump=True, jump_times=2)
    else:
        teleport('up')


class RopeLift(Command):
    """Performs a RopeLift."""

    def __init__(self, jump='False'):
        super().__init__(locals())
        self.jump = settings.validate_boolean(jump)

    def main(self):
        print(f"{self.jump}")
        if self.jump:
            time.sleep(0.1)
            press(Key.JUMP)
        press(Key.ROPE_LIFT, 2)
        time.sleep(1.2)
        if self.jump:
            time.sleep(0.3)


def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    if config.stage_fright and direction != 'up' and utils.bernoulli(0.75):
        utils.sleep_in_floating(utils.rand_float(0.1, 0.3))
    d_y = target[1] - config.player_pos[1]
    if direction == 'down':
        press(Key.JUMP, 3)
    elif direction == 'up':
        up(d_y)
        return
    teleport(direction)


class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def get_tolerance(self):
        return settings.adjust_tolerance if self.custom_tolerance is None else float(self.custom_tolerance)

    def __init__(self, x, y, max_steps=5, custom_tolerance=None):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_non_negative_int(max_steps)
        self.custom_tolerance = settings.validate_float(custom_tolerance, nullable=True)

    def main(self):
        counter = self.max_steps
        toggle = True
        error = utils.distance(config.player_pos, self.target)
        while config.enabled and counter > 0 and error > self.get_tolerance():
            if toggle:
                d_x = self.target[0] - config.player_pos[0]
                threshold = self.get_tolerance() / math.sqrt(2)
                if abs(d_x) > threshold:
                    walkOrTeleport(d_x, threshold, self.target[0])
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > self.get_tolerance() / math.sqrt(2):
                    if d_y < 0:
                        up(d_y)
                    else:
                        key_down('down')
                        utils.sleep_in_floating(0.05)
                        press(Key.JUMP, 3, down_time=0.1)
                        key_up('down')
                        utils.sleep_in_floating(0.05)
                    counter -= 1
            error = utils.distance(config.player_pos, self.target)
            toggle = not toggle


def walkOrTeleport(d_x, threshold, target):
    walk_counter = 0
    if d_x < 0:
        key_down('left')
        if d_x <= horizon_teleport_distance:
            while config.enabled and d_x < -1 * threshold and walk_counter < 60:
                utils.sleep_in_floating(0.05)
                walk_counter += 1
                d_x = target - config.player_pos[0]
            key_up('left')
        else:
            teleport('left')
    else:
        key_down('right')
        if d_x <= horizon_teleport_distance:
            while config.enabled and d_x > threshold and walk_counter < 60:
                utils.sleep_in_floating(0.05)
                walk_counter += 1
                d_x = target - config.player_pos[0]
            key_up('right')
        else:
            teleport('right')


class Buff(Command):
    """Uses each of Shadowers's buffs once."""

    def __init__(self):
        super().__init__(locals())
        self.cd120_buff_time = 0
        self.cd180_buff_time = 0
        self.cd200_buff_time = 0
        self.cd240_buff_time = 0
        self.cd900_buff_time = 0
        self.decent_buff_time = 0

    def main(self):
        # buffs = [Key.SPEED_INFUSION, Key.HOLY_SYMBOL, Key.SHARP_EYE, Key.COMBAT_ORDERS, Key.ADVANCED_BLESSING]
        # now = time.time()
        #
        # if self.cd120_buff_time == 0 or now - self.cd120_buff_time > 120:
        #     press(Key.EPIC_ADVENTURE, 2)
        #     self.cd120_buff_time = now
        # if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 180:
        #     self.cd180_buff_time = now
        # if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
        #     press(Key.SHADOW_PARTNER, 2)
        #     self.cd200_buff_time = now
        # if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
        #     self.cd240_buff_time = now
        # if self.cd900_buff_time == 0 or now - self.cd900_buff_time > 900:
        #     press(Key.MAPLE_WARRIOR, 2)
        #     self.cd900_buff_time = now
        # if self.decent_buff_time == 0 or now - self.decent_buff_time > settings.buff_cooldown:
        #     for key in buffs:
        #         press(key, 3, up_time=0.3)
        #     self.decent_buff_time = now
        pass


class Teleport(Command):
    """
    Teleports in a given direction, jumping if specified. Adds the player's position
    to the current Layout if necessary.
    """

    def __init__(self, direction, jump='False', jump_times=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.jump_times = settings.validate_positive_int(jump_times)

    def main(self):
        teleport(self.direction, self.jump, self.jump_times)


def teleport(direction, jump=None, jump_times=1):
    num_presses = 3
    utils.sleep_in_floating(0.05)
    if jump is None and direction == 'up':
        jump = True
    elif jump is None:
        jump = False
    if direction in ['up', 'down']:
        num_presses = 2
    if direction != 'up':
        key_down(direction)
        utils.sleep_in_floating(0.05)
    if jump:
        if direction == 'down':
            press(Key.JUMP, 3, down_time=0.1)
        if direction == 'up':
            press(Key.JUMP, 1, down_time=0.01, up_time=0.01)
    if direction == 'up':
        key_down(direction)
        if jump and jump_times > 1:
            utils.sleep_in_floating(0.02)
            press(Key.JUMP, jump_times, down_time=0.01, up_time=0.01)
            utils.sleep_in_floating(jump_times * 0.015)
        utils.sleep_in_floating(0.05)
    press(Key.TELEPORT, num_presses)
    key_up(direction)
    utils.sleep_in_floating(0.05)
    if settings.record_layout:
        config.layout.add(*config.player_pos)


class BigBang(Command):
    """Attacks using 'BigBang' in a given direction."""

    def __init__(self, direction=None, attacks=2, repetitions=1, jump='False', tp_before=None, tp_after=None):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction, nullable=True)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)
        self.jump = settings.validate_boolean(jump)
        self.tp_before = settings.validate_arrows(tp_before, nullable=True)
        self.tp_after = settings.validate_arrows(tp_after, nullable=True)

    def main(self):
        utils.sleep_in_floating(0.05)
        if self.direction:
            key_down(self.direction)
            utils.sleep_in_floating(0.05)
        if self.tp_before:
            teleport(self.tp_before)
        if config.stage_fright and utils.bernoulli(0.7):
            utils.sleep_in_floating(utils.rand_float(0.1, 0.3))
        if self.jump:
            press(Key.JUMP, 2)
        for _ in range(self.repetitions):
            press(Key.BIG_BANG, self.attacks, up_time=0.05)
        if self.tp_after:
            teleport(self.tp_after)
        if self.direction:
            key_up(self.direction)
        if not self.tp_after:
            if self.attacks > 2:
                utils.sleep_in_floating(0.3)
            else:
                utils.sleep_in_floating(0.2)


def normal_skill(key, direction, jump, tp_before, tp_after, num_press=3):
    utils.sleep_in_floating(0.05)
    if tp_before:
        teleport(tp_before)
    if direction:
        key_down(direction)
        utils.sleep_in_floating(0.05)
    if jump:
        press(Key.JUMP, 1, down_time=0.1, up_time=0.15)
    press(key, num_press, down_time=0.05, up_time=0.05)
    if tp_after:
        teleport(tp_after)
    if direction:
        key_up(direction)


class Peacemaker(Command):
    """Attacks using 'Peacemaker' in a given direction."""

    def __init__(self, direction=None, num_press=1, jump='False', tp_before=None, tp_after=None):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump = settings.validate_boolean(jump)
        self.tp_before = settings.validate_arrows(tp_before, nullable=True)
        self.tp_after = settings.validate_arrows(tp_after, nullable=True)

    def main(self):
        normal_skill(Key.PEACEMAKER, self.direction, self.jump, self.tp_before, self.tp_after, num_press=self.num_press)
        utils.sleep_in_floating(0.2)


class Genesis(Command):
    """Attacks using 'Genesis' in a given direction."""

    def __init__(self, direction=None, jump='False', tp_before=None, tp_after=None):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.jump = settings.validate_boolean(jump)
        self.tp_before = settings.validate_arrows(tp_before, nullable=True)
        self.tp_after = settings.validate_arrows(tp_after, nullable=True)

    def main(self):
        normal_skill(Key.GENESIS, self.direction, self.jump, self.tp_before, self.tp_after)
        utils.sleep_in_floating(0.2)


class HeavensDoor(Command):
    """Attacks using 'HeavensDoor' in a given direction."""

    def __init__(self, direction=None, jump='False', tp_before=None, tp_after=None):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.jump = settings.validate_boolean(jump)
        self.tp_before = settings.validate_arrows(tp_before, nullable=True)
        self.tp_after = settings.validate_arrows(tp_after, nullable=True)

    def main(self):
        normal_skill(Key.HEAVENS_DOOR, self.direction, self.jump, self.tp_before, self.tp_after)
        utils.sleep_in_floating(0.2)


class FountainOfVengeance(Command):
    """Attacks using 'FountainOfVengeance' in a given direction."""

    def __init__(self, direction=None, tp_before=None, tp_after=None):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.tp_before = settings.validate_arrows(tp_before, nullable=True)
        self.tp_after = settings.validate_arrows(tp_after, nullable=True)

    def main(self):
        normal_skill(Key.FOUNTAIN_OF_VENGEANCE, self.direction, False, self.tp_before, self.tp_after)
        utils.sleep_in_floating(0.2)


class HolyAdvent(Command):
    """Attacks using 'HolyAdvent' in a given direction."""

    def __init__(self, direction=None, tp_before=None, tp_after=None):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.tp_before = settings.validate_arrows(tp_before, nullable=True)
        self.tp_after = settings.validate_arrows(tp_after, nullable=True)

    def main(self):
        normal_skill(Key.HOLY_ADVENT, self.direction, False, self.tp_before, self.tp_after)
        utils.sleep_in_floating(0.2)


class Infinity(Command):
    """Attacks using 'Infinity' in a given direction."""

    def __init__(self, direction=None, tp_before=None, tp_after=None):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.tp_before = settings.validate_arrows(tp_before, nullable=True)
        self.tp_after = settings.validate_arrows(tp_after, nullable=True)

    def main(self):
        normal_skill(Key.INFINITY, self.direction, False, self.tp_before, self.tp_after)
        utils.sleep_in_floating(0.2)


class UnreliableMemory(Command):
    """Attacks using 'UnreliableMemory' in a given direction."""

    def __init__(self, direction=None, tp_before=None, tp_after=None):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.tp_before = settings.validate_arrows(tp_before, nullable=True)
        self.tp_after = settings.validate_arrows(tp_after, nullable=True)

    def main(self):
        normal_skill(Key.UNRELIABLE_MEMORY, self.direction, False, self.tp_before, self.tp_after)
        utils.sleep_in_floating(0.2)


class AngelOfBalance(Command):
    """Attacks using 'UnreliableMemory' in a given direction."""

    def __init__(self, direction=None, tp_before=None, tp_after=None):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.tp_before = settings.validate_arrows(tp_before, nullable=True)
        self.tp_after = settings.validate_arrows(tp_after, nullable=True)

    def main(self):
        normal_skill(Key.ANGEL_OF_BALANCE, self.direction, False, self.tp_before, self.tp_after)
        utils.sleep_in_floating(0.2)


class Benediction(Command):
    """Attacks using 'UnreliableMemory' in a given direction."""

    def __init__(self, direction=None, tp_before=None, tp_after=None):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.tp_before = settings.validate_arrows(tp_before, nullable=True)
        self.tp_after = settings.validate_arrows(tp_after, nullable=True)

    def main(self):
        normal_skill(Key.BENEDICTION, self.direction, False, self.tp_before, self.tp_after)
        utils.sleep_in_floating(0.2)


class TermsAndConditions(Command):
    """Attacks using 'UnreliableMemory' in a given direction."""

    def __init__(self, direction=None, tp_before=None, tp_after=None):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.tp_before = settings.validate_arrows(tp_before, nullable=True)
        self.tp_after = settings.validate_arrows(tp_after, nullable=True)

    def main(self):
        normal_skill(Key.TERMS_AND_CONDITIONS, self.direction, False, self.tp_before, self.tp_after)
        utils.sleep_in_floating(0.2)


class SolJanus(Command):
    """
    Uses 'DarkFlare' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None, tp_before=None, tp_after=None):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.tp_before = settings.validate_arrows(tp_before, nullable=True)
        self.tp_after = settings.validate_arrows(tp_after, nullable=True)

    def main(self):
        if self.tp_before:
            teleport(self.tp_before)
        if self.direction:
            press(self.direction, 1, down_time=0.1, up_time=0.05)
        press(Key.SOL_JANUS, 3)
        if self.tp_after:
            teleport(self.tp_after)


class ErdaShower(Command):
    """
    Use ErdaShower in a given direction, Placing ErdaFountain if specified. Adds the player's position
    to the current Layout if necessary.
    """

    def __init__(self, direction=None, jump='False', use_erda_foundation='False', tp_before=None, tp_after=None):
        super().__init__(locals())
        if direction is not None:
            self.direction = settings.validate_arrows(direction)
        else:
            self.direction = None
        self.jump = settings.validate_boolean(jump)
        self.use_erda_foundation = settings.validate_boolean(use_erda_foundation)
        self.tp_before = settings.validate_arrows(tp_before, nullable=True)
        self.tp_after = settings.validate_arrows(tp_after, nullable=True)

    def main(self):
        if self.tp_before:
            teleport(self.tp_before)
        if self.use_erda_foundation:
            press(Key.ERDA_SHOWER, 3)
        else:
            num_presses = 3
            time.sleep(0.05)

            if self.direction in ['up', 'down']:
                num_presses = 2
            if self.direction is not None and self.direction != 'up':
                key_down(self.direction)
                time.sleep(0.05)
            if self.jump:
                if self.direction == 'down':
                    press(Key.JUMP, 3, down_time=0.1)
                else:
                    press(Key.JUMP, 1)
            if self.direction == 'up':
                key_down(self.direction)
                time.sleep(0.05)

            press(Key.ERDA_SHOWER, num_presses)
            if self.direction is not None:
                key_up(self.direction)
            if self.tp_after:
                teleport(self.tp_after)

        if settings.record_layout:
            config.layout.add(*config.player_pos)
