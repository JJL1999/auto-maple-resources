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
    ROPE_LIFT = 'v'

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
    QUINTUPLE_STAR = 'a'
    SHADOW_BITE = 'r'
    GREATER_DARK_SERVANT = 'w'
    DARK_OMEN = 's'
    SHADOW_DODGE = 'f'
    RAPID_THROW = 'e'
    PHALANX_CHARGE = 'g'
    SHADOW_SPEAR = 'f1'
    SILENCE = 'f4'
    DARK_ELEMENTAL = '0'
    SHADOW_BAT = '9'

    # Commons
    ERDA_SHOWER = 't'
    SOL_JANUS = 'i'
    TRUE_ARACHNID_REFLECTION = 'u'
    SOLAR_CREST = 'h'

    # Common Buffs
    HERO_ECHO = 'f8'
    G_BUFF_CRI = 'f5'
    G_BUFF_DAM = 'f6'
    HYPER_BUFF_DAM = 'f2'
    GODDESS_BUFF = 'f3'


#########################
#       Commands        #
#########################
flash_jump_distance = 1.1 * settings.move_tolerance
jump_and_attack = None


def up(dy):
    if abs(dy) > flash_jump_distance:
        jump = 'True' if abs(dy) > 1.4 * settings.move_tolerance else 'False'
        print(f"dy={dy}, 1.6*move_tolerance={1.6 * settings.move_tolerance}, jump={jump}")
        RopeLift(jump=jump).main()
    else:
        FlashJump('up', 2).main()
    utils.sleep_in_floating(0.3)


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
        time.sleep(0.5)
    elif direction == 'up':
        up(d_y)
    if jump_and_attack is None or direction == 'up':
        press(Key.JUMP, num_presses)
    else:
        jump_and_attack.main()
    time.sleep(0.5)


class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def get_tolerance(self):
        return settings.adjust_tolerance if self.custom_tolerance is None else float(self.custom_tolerance)

    def __init__(self, x, y, max_steps=5, custom_tolerance=None):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_positive_int(max_steps)
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
                if abs(d_y) > self.get_tolerance() / math.sqrt(2):
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
            time.sleep(0.3)


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

    def __init__(self, direction, jump_times=2):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump_times = settings.validate_positive_int(jump_times)

    @staticmethod
    def flash_jump(direction, jump_times, wait_time=None):
        if jump_times <= 0:
            return
        if direction != 'up':
            if direction:
                key_down(direction)
            press(Key.JUMP, 1, down_time=0.02, up_time=0.02)
        else:
            press(Key.JUMP, 1, down_time=0.02, up_time=0.0)
            if direction:
                key_down(direction)
        press(Key.JUMP, jump_times - 1, down_time=0.02, up_time=0.02)
        if direction:
            key_up(direction)
        if wait_time is not None:
            utils.sleep_in_floating(wait_time)
        else:
            utils.sleep_in_floating(jump_times * 0.03)

    @staticmethod
    def up_jump_and_flash_jump(direction, jump_times, wait_time=0.4):
        FlashJump.flash_jump('up', 3, 0.01)
        key_down(direction)
        utils.sleep_in_floating(0.1)
        if jump_times > 0:
            press(Key.JUMP, jump_times - 1, up_time=0.02, down_time=0.02)
        key_up(direction)
        utils.sleep_in_floating(wait_time)

    def main(self):
        self.flash_jump(self.direction, self.jump_times)


class RopeLift(Command):
    """Performs a flash jump in the given direction."""

    def __init__(self, jump='False', wait_time=1.2):
        super().__init__(locals())
        self.jump = settings.validate_boolean(jump)
        self.wait_time = settings.validate_float(wait_time)

    def main(self):
        print(f"{self.jump}")
        if self.jump:
            time.sleep(0.1)
            press(Key.JUMP)
        press(Key.ROPE_LIFT, 2)
        time.sleep(self.wait_time)
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


def execute_general_skill_template(key, direction=None, jump_times=0, up_jump_and_flash_jump=False, walk_time=0, num_press=3,
                                   repetitions=1):
    for _ in range(repetitions):
        flash_jumped = False
        if direction and direction != 'up':
            key_down(direction)
        if walk_time != 0:
            utils.sleep_in_floating(walk_time)
        if up_jump_and_flash_jump:
            FlashJump.up_jump_and_flash_jump(direction, jump_times, 0.05)
        elif jump_times >= 1:
            FlashJump.flash_jump(direction, jump_times, 0.05)
            flash_jumped = True
        press(key, num_press, down_time=0.01, up_time=0.01)
        if direction:
            key_up(direction)
        if flash_jumped:
            utils.sleep_in_floating(0.1)


class QuintupleStar(Command):
    """Attacks using 'CruelStab' in a given direction."""

    def __init__(self, direction=None, up_jump_and_flash_jump='False',
                 jump_times=0, walk_time=0, num_press=3, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction, nullable=True)
        self.up_jump_and_flash_jump = settings.validate_boolean(up_jump_and_flash_jump)
        self.jump_times = settings.validate_non_negative_int(jump_times)
        self.walk_time = settings.validate_float(walk_time)
        self.num_press = settings.validate_positive_int(num_press)
        self.repetitions = settings.validate_positive_int(repetitions)

    def main(self):
        execute_general_skill_template(Key.QUINTUPLE_STAR, self.direction,
                                       up_jump_and_flash_jump=self.up_jump_and_flash_jump,
                                       jump_times=self.jump_times, walk_time=self.walk_time,
                                       num_press=self.num_press, repetitions=self.repetitions)


jump_and_attack = QuintupleStar(jump_times=2)


class GreaterDarkServant(Command):
    """
    Uses 'GreaterDarkServant' in a given direction
    """

    def __init__(self, direction=None, up_jump_and_flash_jump='False',
                 jump_times=0, walk_time=0, num_press=3, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction, nullable=True)
        # self.up_jump_and_flash_jump = settings.validate_boolean(up_jump_and_flash_jump)
        # self.jump_times = settings.validate_non_negative_int(jump_times)
        self.walk_time = settings.validate_float(walk_time)
        self.num_press = settings.validate_positive_int(num_press)
        self.repetitions = settings.validate_positive_int(repetitions)

    def main(self):
        execute_general_skill_template(Key.GREATER_DARK_SERVANT, self.direction,
                                       # up_jump_and_flash_jump=self.up_jump_and_flash_jump,
                                       # jump_times=self.jump_times,
                                       walk_time=self.walk_time,
                                       num_press=self.num_press, repetitions=self.repetitions)


class ShadowDodge(Command):
    """
    Uses 'ShadowDodge' in a given direction
    """

    def __init__(self, true_direction, up_jump_and_flash_jump='False',
                 jump_times=0, walk_time=0, num_press=3, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(true_direction, nullable=True)
        # Get the reverse horizontal direction
        if self.direction is not None:
            self.direction = 'right' if self.direction == 'left' else (
                'left' if self.direction == 'right' else self.direction
            )
        self.up_jump_and_flash_jump = settings.validate_boolean(up_jump_and_flash_jump)
        self.jump_times = settings.validate_non_negative_int(jump_times)
        self.walk_time = settings.validate_float(walk_time)
        self.num_press = settings.validate_positive_int(num_press)
        self.repetitions = settings.validate_positive_int(repetitions)

    def main(self):
        time.sleep(0.05)
        d = self.direction
        if self.direction and self.direction == 'left' or self.direction == 'right':
            d = None
            key_down(self.direction)
            utils.sleep_in_floating(0.05)
            key_up(self.direction)
        execute_general_skill_template(Key.SHADOW_DODGE, d,
                                       up_jump_and_flash_jump=self.up_jump_and_flash_jump,
                                       jump_times=self.jump_times, walk_time=self.walk_time,
                                       num_press=self.num_press, repetitions=self.repetitions)


class DarkOmen(Command):
    """
    Uses 'DarkOmen' in a given direction
    """

    def __init__(self, direction=None, up_jump_and_flash_jump='False',
                 jump_times=0, walk_time=0, num_press=3, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction, nullable=True)
        self.up_jump_and_flash_jump = settings.validate_boolean(up_jump_and_flash_jump)
        self.jump_times = settings.validate_non_negative_int(jump_times)
        self.walk_time = settings.validate_float(walk_time)
        self.num_press = settings.validate_positive_int(num_press)
        self.repetitions = settings.validate_positive_int(repetitions)

    def main(self):
        execute_general_skill_template(Key.DARK_OMEN, self.direction,
                                       up_jump_and_flash_jump=self.up_jump_and_flash_jump,
                                       jump_times=self.jump_times, walk_time=self.walk_time,
                                       num_press=self.num_press, repetitions=self.repetitions)


class ShadowBite(Command):
    """
    Uses 'ShadowBite' in a given direction
    """

    def __init__(self, direction=None, up_jump_and_flash_jump='False',
                 jump_times=0, walk_time=0, num_press=3, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction, nullable=True)
        self.up_jump_and_flash_jump = settings.validate_boolean(up_jump_and_flash_jump)
        self.jump_times = settings.validate_non_negative_int(jump_times)
        self.walk_time = settings.validate_float(walk_time)
        self.num_press = settings.validate_positive_int(num_press)
        self.repetitions = settings.validate_positive_int(repetitions)

    def main(self):
        execute_general_skill_template(Key.SHADOW_BITE, self.direction,
                                       up_jump_and_flash_jump=self.up_jump_and_flash_jump,
                                       jump_times=self.jump_times, walk_time=self.walk_time,
                                       num_press=self.num_press, repetitions=self.repetitions)


class RapidThrow(Command):
    """
    Uses 'ShadowBite' in a given direction
    """

    def __init__(self, direction=None, up_jump_and_flash_jump='False',
                 jump_times=0, walk_time=0, num_press=3, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction, nullable=True)
        self.up_jump_and_flash_jump = settings.validate_boolean(up_jump_and_flash_jump)
        self.jump_times = settings.validate_non_negative_int(jump_times)
        self.walk_time = settings.validate_float(walk_time)
        self.num_press = settings.validate_positive_int(num_press)
        self.repetitions = settings.validate_positive_int(repetitions)

    def main(self):
        execute_general_skill_template(Key.RAPID_THROW, self.direction,
                                       up_jump_and_flash_jump=self.up_jump_and_flash_jump,
                                       jump_times=self.jump_times, walk_time=self.walk_time,
                                       num_press=self.num_press, repetitions=self.repetitions)


class PhalanxCharge(Command):
    """
    Uses 'PhalanxCharge' in a given direction
    """

    def __init__(self, direction=None, up_jump_and_flash_jump='False',
                 jump_times=0, walk_time=0, num_press=1, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction, nullable=True)
        self.up_jump_and_flash_jump = settings.validate_boolean(up_jump_and_flash_jump)
        self.jump_times = settings.validate_non_negative_int(jump_times)
        self.walk_time = settings.validate_float(walk_time)
        self.num_press = settings.validate_positive_int(num_press)
        self.repetitions = settings.validate_positive_int(repetitions)

    def main(self):
        execute_general_skill_template(Key.PHALANX_CHARGE, self.direction,
                                       up_jump_and_flash_jump=self.up_jump_and_flash_jump,
                                       jump_times=self.jump_times, walk_time=self.walk_time,
                                       num_press=self.num_press, repetitions=self.repetitions)


class ShadowSpear(Command):
    """
    Uses 'PhalanxCharge' in a given direction
    """

    def __init__(self, direction=None, up_jump_and_flash_jump='False',
                 jump_times=0, walk_time=0, num_press=3, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction, nullable=True)
        self.up_jump_and_flash_jump = settings.validate_boolean(up_jump_and_flash_jump)
        self.jump_times = settings.validate_non_negative_int(jump_times)
        self.walk_time = settings.validate_float(walk_time)
        self.num_press = settings.validate_positive_int(num_press)
        self.repetitions = settings.validate_positive_int(repetitions)

    def main(self):
        execute_general_skill_template(Key.SHADOW_SPEAR, self.direction,
                                       up_jump_and_flash_jump=self.up_jump_and_flash_jump,
                                       jump_times=self.jump_times, walk_time=self.walk_time,
                                       num_press=self.num_press, repetitions=self.repetitions)


class Silence(Command):
    """
    Uses 'PhalanxCharge' in a given direction
    """

    def __init__(self, direction=None, up_jump_and_flash_jump='False',
                 jump_times=0, walk_time=0, num_press=3, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction, nullable=True)
        self.up_jump_and_flash_jump = settings.validate_boolean(up_jump_and_flash_jump)
        self.jump_times = settings.validate_non_negative_int(jump_times)
        self.walk_time = settings.validate_float(walk_time)
        self.num_press = settings.validate_positive_int(num_press)
        self.repetitions = settings.validate_positive_int(repetitions)

    def main(self):
        execute_general_skill_template(Key.SILENCE, self.direction,
                                       up_jump_and_flash_jump=self.up_jump_and_flash_jump,
                                       jump_times=self.jump_times, walk_time=self.walk_time,
                                       num_press=self.num_press, repetitions=self.repetitions)


class DarkElemental(Command):
    """
    Uses 'PhalanxCharge' in a given direction
    """

    def __init__(self, direction=None, up_jump_and_flash_jump='False',
                 jump_times=0, walk_time=0, num_press=1, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction, nullable=True)
        self.up_jump_and_flash_jump = settings.validate_boolean(up_jump_and_flash_jump)
        self.jump_times = settings.validate_non_negative_int(jump_times)
        self.walk_time = settings.validate_float(walk_time)
        self.num_press = settings.validate_positive_int(num_press)
        self.repetitions = settings.validate_positive_int(repetitions)

    def main(self):
        execute_general_skill_template(Key.DARK_ELEMENTAL, self.direction,
                                       up_jump_and_flash_jump=self.up_jump_and_flash_jump,
                                       jump_times=self.jump_times, walk_time=self.walk_time,
                                       num_press=self.num_press, repetitions=self.repetitions)


class ShadowBat(Command):
    """
    Uses 'PhalanxCharge' in a given direction
    """

    def __init__(self, direction=None, up_jump_and_flash_jump='False',
                 jump_times=0, walk_time=0, num_press=1, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction, nullable=True)
        self.up_jump_and_flash_jump = settings.validate_boolean(up_jump_and_flash_jump)
        self.jump_times = settings.validate_non_negative_int(jump_times)
        self.walk_time = settings.validate_float(walk_time)
        self.num_press = settings.validate_positive_int(num_press)
        self.repetitions = settings.validate_positive_int(repetitions)

    def main(self):
        execute_general_skill_template(Key.SHADOW_BAT, self.direction,
                                       up_jump_and_flash_jump=self.up_jump_and_flash_jump,
                                       jump_times=self.jump_times, walk_time=self.walk_time,
                                       num_press=self.num_press, repetitions=self.repetitions)


class SolJanus(Command):
    """
    Uses 'SolJanus' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    def main(self):
        execute_general_skill_template(Key.SOL_JANUS, self.direction,
                                       jump_times=self.jump_times,
                                       num_press=self.num_press)


class ErdaShower(Command):
    """
    Uses 'SolJanus' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    def main(self):
        execute_general_skill_template(Key.ERDA_SHOWER, self.direction,
                                       jump_times=self.jump_times,
                                       num_press=self.num_press)


class TrueArachnidReflection(Command):
    """
    Uses 'SolJanus' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    def main(self):
        execute_general_skill_template(Key.TRUE_ARACHNID_REFLECTION, self.direction,
                                       jump_times=self.jump_times,
                                       num_press=self.num_press)


class SolarCrest(Command):
    """
    Uses 'SolJanus' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    def main(self):
        execute_general_skill_template(Key.SOLAR_CREST, self.direction,
                                       jump_times=self.jump_times,
                                       num_press=self.num_press)


class HeroEcho(Command):
    """
    Uses 'SolJanus' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    def main(self):
        execute_general_skill_template(Key.HERO_ECHO, self.direction,
                                       jump_times=self.jump_times,
                                       num_press=self.num_press)


class GuildBuffCriticalDamage(Command):
    """
    Uses 'SolJanus' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    def main(self):
        execute_general_skill_template(Key.G_BUFF_CRI, self.direction,
                                       jump_times=self.jump_times,
                                       num_press=self.num_press)


class GuildBuffDamage(Command):
    """
    Uses 'SolJanus' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    def main(self):
        execute_general_skill_template(Key.G_BUFF_DAM, self.direction,
                                       jump_times=self.jump_times,
                                       num_press=self.num_press)


class HyperSkillDamage(Command):
    """
    Uses 'SolJanus' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    def main(self):
        execute_general_skill_template(Key.HYPER_BUFF_DAM, self.direction,
                                       jump_times=self.jump_times,
                                       num_press=self.num_press)


class GoddessBuff(Command):
    """
    Uses 'SolJanus' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    def main(self):
        execute_general_skill_template(Key.GODDESS_BUFF, self.direction,
                                       jump_times=self.jump_times,
                                       num_press=self.num_press)
