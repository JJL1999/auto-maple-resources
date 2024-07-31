"""A collection of all commands that Shadower can use to interact with the game. 	"""

import math
import time

from src.common import config, settings, utils
from src.common.vkeys import press, key_down, key_up
from src.routine.components import Command


# List of key mappings
class Key:
    # Movement
    JUMP = 'space'
    FLASH_JUMP = 'shift'
    ROPE_LIFT = 'c'

    # Buffs
    # SHADOW_PARTNER = '1'
    # MAPLE_WARRIOR = '2'
    # EPIC_ADVENTURE = '3'
    # SPEED_INFUSION = '8'
    # HOLY_SYMBOL = '4'
    # SHARP_EYE = '5'
    # COMBAT_ORDERS = '6'
    # ADVANCED_BLESSING = '7'
    # SUMMON_FAMILIARS = 'page down'
    # FAMILIAR_ESSENCE = '6'

    # Skills
    SHOWDOWN = 'd'
    SUDDEN_RAID = 'g'
    DARK_FLARE = '`'
    SOL_JANUS = 'i'
    DARK_LORDS_OMEN = 'r'
    SHADOW_LEAP = 's'
    SHADOW_SURGE = 'f'
    ERDA_SHOWER = 't'
    DEATH_STAR = 'e'
    SHURRIKANE = 'w'


#########################
#       Commands        #
#########################
flash_jump_distance = 0.8 * settings.move_tolerance


def up(dy):
    print("============= up")
    if abs(dy) > flash_jump_distance:
        jump = 'True' if abs(dy) > 1.6 * settings.move_tolerance else 'False'
        print(f"dy={dy}, 1.6*move_tolerance={1.6*settings.move_tolerance}, jump={jump}")
        RopeLift(jump).main()
    else:
        FlashJump('up', 3).main()


def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    num_presses = 2
    if direction == 'up' or direction == 'down':
        num_presses = 0
    if config.stage_fright and direction != 'up' and utils.bernoulli(0.75):
        time.sleep(utils.rand_float(0.1, 0.3))
    d_y = target[1] - config.player_pos[1]
    if direction == 'down':
        press(Key.JUMP, 3)
        time.sleep(1)
    elif direction == 'up':
        up(d_y)
    press(Key.JUMP, num_presses)
    time.sleep(0.5)


class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_positive_int(max_steps)

    def main(self):
        counter = self.max_steps
        toggle = True
        error = utils.distance(config.player_pos, self.target)
        while config.enabled and counter > 0 and error > settings.adjust_tolerance:
            if toggle:
                d_x = self.target[0] - config.player_pos[0]
                threshold = settings.adjust_tolerance / math.sqrt(2)
                if abs(d_x) > threshold:
                    walk_counter = 0
                    if d_x < 0:
                        key_down('left')
                        while config.enabled and d_x < -1 * threshold and walk_counter < 60:
                            time.sleep(0.05)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right')
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            time.sleep(0.05)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > settings.adjust_tolerance / math.sqrt(2):
                    if d_y < 0:
                        up(d_y)
                    else:
                        key_down('down')
                        time.sleep(0.05)
                        press(Key.JUMP, 3, down_time=0.1)
                        key_up('down')
                        time.sleep(0.05)
                    counter -= 1
            error = utils.distance(config.player_pos, self.target)
            toggle = not toggle
            time.sleep(0.2)


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


class FlashJump(Command):
    """Performs a flash jump in the given direction."""

    def __init__(self, direction, jump_times=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    def main(self):
        time.sleep(0.1)
        if self.direction == 'up':
            press(Key.SHADOW_LEAP, 1)
        else:
            key_down(self.direction)
            press(Key.JUMP, 1)
            press(Key.JUMP, self.jump_times)
            key_up(self.direction)
        time.sleep(0.5)


class ShadowLeap(Command):
    """Performs a flash jump in the given direction."""

    def __init__(self):
        super().__init__(locals())

    def main(self):
        press(Key.SHADOW_LEAP, 1)
        time.sleep(0.4)


class RopeLift(Command):
    """Performs a flash jump in the given direction."""

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


class KeyControl(Command):
    """Performs a flash jump in the given direction."""

    def __init__(self, key, is_up):
        super().__init__(locals())
        self.key = key
        self.is_up = settings.validate_boolean(is_up)

    def main(self):
        if self.is_up:
            key_up(self.key)
        else:
            key_down(self.key)
        time.sleep(0.1)


class Showdown(Command):
    """Attacks using 'CruelStab' in a given direction."""

    def __init__(self, direction, attacks=2, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)

    def main(self):
        time.sleep(0.05)
        key_down(self.direction)
        time.sleep(0.05)
        if config.stage_fright and utils.bernoulli(0.7):
            time.sleep(utils.rand_float(0.1, 0.3))
        for _ in range(self.repetitions):
            press(Key.SHOWDOWN, self.attacks, up_time=0.05)
        key_up(self.direction)
        if self.attacks > 2:
            time.sleep(0.3)
        else:
            time.sleep(0.2)


class ShowdownRandomDirection(Command):
    """Uses 'CruelStab' once."""

    def main(self):
        press(Key.SHOWDOWN, 1, up_time=0.05)


class DarkFlare(Command):
    """
    Uses 'DarkFlare' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.direction:
            press(self.direction, 1, down_time=0.1, up_time=0.05)
        press(Key.DARK_FLARE, 3)


class SolJanus(Command):
    """
    Uses 'DarkFlare' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.direction:
            press(self.direction, 1, down_time=0.1, up_time=0.05)
        press(Key.SOL_JANUS, 3)


class ShadowSurge(Command):
    """
    Uses 'DarkFlare' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None):
        super().__init__(locals())
        self.direction = None
        if direction is not None:
            self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.direction:
            key_down(self.direction)
        press(Key.SHADOW_SURGE, 1)
        if self.direction:
            key_up(self.direction)


class DarkLordsOmen(Command):
    """
    Uses 'ShadowVeil' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.direction:
            press(self.direction, 1, down_time=0.1, up_time=0.05)
        else:
            if config.player_pos[0] > 0.5:
                press('left', 1, down_time=0.1, up_time=0.05)
            else:
                press('right', 1, down_time=0.1, up_time=0.05)
        press(Key.DARK_LORDS_OMEN, 3)


class ErdaShower(Command):
    """
    Use ErdaShower in a given direction, Placing ErdaFountain if specified. Adds the player's position
    to the current Layout if necessary.
    """

    def __init__(self, direction=None, jump='False', use_erda_foundation='False'):
        super().__init__(locals())
        if direction is not None:
            self.direction = settings.validate_arrows(direction)
        else:
            self.direction = None
        self.jump = settings.validate_boolean(jump)
        self.use_erda_foundation = settings.validate_boolean(use_erda_foundation)

    def main(self):
        if self.use_erda_foundation:
            press(Key.ERDA_SHOWER, 3)
        else:
            num_presses = 3
            time.sleep(0.05)

            if self.direction in ['up', 'down']:
                num_presses = 2
            if self.direction != 'up':
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
            key_up(self.direction)

        if settings.record_layout:
            config.layout.add(*config.player_pos)


class SuddenRaid(Command):
    """Uses 'SuddenRaid' once."""

    def main(self):
        press(Key.SUDDEN_RAID, 3)


class DeathStar(Command):
    """Uses 'True Arachnid Reflection' once."""

    def main(self):
        press(Key.DEATH_STAR, 3)


class Shurrikane(Command):
    """
    Uses 'TrickBlade' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None, jump='False', re_trigger_time=-1):
        super().__init__(locals())
        if direction is None:
            self.direction = direction
        else:
            self.direction = settings.validate_horizontal_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.re_trigger_time = float(re_trigger_time)

    def main(self):
        if self.direction:
            press(self.direction, 1, down_time=0.1, up_time=0.05)
        else:
            if config.player_pos[0] > 0.5:
                press('left', 1, down_time=0.1, up_time=0.05)
            else:
                press('right', 1, down_time=0.1, up_time=0.05)
        if self.jump:
            press(Key.JUMP, 1)
            time.sleep(0.2)
        press(Key.SHURRIKANE, 1)
        if self.re_trigger_time >= 0:
            time.sleep(self.re_trigger_time)
            press(Key.SHURRIKANE, 1)


class FlashJumpWithShowdownRandomDirection(Command):
    """Performs a flash jump in the given direction."""

    def __init__(self, direction, jump_times=1, low_jump='False', use_shadow_leap='False'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump_times = settings.validate_non_negative_int(jump_times)
        self.low_jump = settings.validate_boolean(low_jump)
        self.use_shadow_leap = settings.validate_boolean(use_shadow_leap)

    def main(self):
        key_down(self.direction)
        time.sleep(0.1)
        delay = 0.01
        if not self.low_jump:
            jump_num = 1
            if self.direction == 'down':
                jump_num += 1
            press(Key.JUMP, jump_num)
            if self.direction == 'up':
                press(Key.SHADOW_LEAP, 1, last_up_time=0.4)
            else:
                press(Key.JUMP, self.jump_times, last_up_time=delay)
        else:
            press(Key.JUMP, down_time=0.05, up_time=0.05)
            press(Key.FLASH_JUMP, self.jump_times, last_up_time=delay)
        time.sleep(0.1)
        if self.use_shadow_leap:
            press(Key.SHADOW_LEAP, 1)
            time.sleep(0.2)
        press(Key.SHOWDOWN, 2, up_time=delay)
        key_up(self.direction)
        time.sleep(0.2 + self.jump_times * 0.1)
