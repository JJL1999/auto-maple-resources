"""A collection of all commands that Shadower can use to interact with the game. 	"""

import math
import time

from src.common import config, settings, utils, high_level_utils
from src.common.vkeys import press, key_down, key_up
from src.routine.components import Command


# List of key mappings
class Key:
    # Movement
    JUMP = 'c'
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
    CHAOS_LOCK = 'q'
    INFERNAL_CONCUSSION = 's'
    DEMON_LASH = 'a'
    ORTHRUS = 'f2'
    DEMON_CRY = 'w'
    BOUNDLESS_RAGE = '`'
    DEMON_IMPACT = 'd'
    DARK_METAMORPHOSIS = 'ctrl'
    DEMON_BANE = 'r'
    CERBERUS_CHOMP = 'g'
    NIGHTMARE = 'f4'
    SPIRIT_OF_RAGE = 'e'
    DEMON_AWAKENING = 'f1'
    BLUE_BLOOD = '0'

    # Commons
    ERDA_SHOWER = 't'
    SOL_JANUS = 'i'


#########################
#       Commands        #
#########################
flash_jump_distance = 1.3 * settings.move_tolerance


def up(dy, target):
    if abs(dy) > flash_jump_distance:
        jump = 'True' if abs(dy) > 1.4 * settings.move_tolerance else 'False'
        print(f"dy={dy}, 1.6*move_tolerance={1.6 * settings.move_tolerance}, jump={jump}")
        RopeLift(jump=jump).main()
    else:
        FlashJump.flash_jump('up', wait_time=0.05)
    if high_level_utils.do_util_matches2(lambda: None, lambda: config.player_pos[1] - target[1], max_wait_time=0.4):
        press(Key.JUMP, up_time=0.05, down_time=0.05)
        utils.sleep_in_floating(0.2)


def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """
    if config.stage_fright and direction != 'up' and utils.bernoulli(0.75):
        time.sleep(utils.rand_float(0.1, 0.3))
    d_y = target[1] - config.player_pos[1]
    if direction == 'up':
        up(d_y, target)
    else:
        FlashJump.flash_jump(direction)


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
                        up(d_y, self.target)
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

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    @staticmethod
    def flash_jump(direction, wait_time=0.3):
        if direction != 'up':
            key_down(direction)
            key_down(Key.JUMP)
        else:
            key_down(Key.JUMP)
            key_down(direction)
        if direction != 'down':
            press(direction, 3, down_time=0.001, up_time=0.001)
        else:
            press(Key.JUMP, 3, down_time=0.001, up_time=0.001)
        key_up(direction)
        key_up(Key.JUMP)
        utils.sleep_in_floating(wait_time)

    def main(self):
        self.flash_jump(self.direction)


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


def normal_skill(key, direction, jump_times=0, walk_time=0, num_press=3):
    utils.sleep_in_floating(0.05)
    flash_jumped = False
    if direction:
        key_down(direction)
    if walk_time == 0:
        utils.sleep_in_floating(0.05)
    else:
        utils.sleep_in_floating(walk_time)
    if jump_times == 1:
        press(Key.JUMP, 1, down_time=0.1, up_time=0.15)
    elif jump_times >= 2 and direction is not None:
        FlashJump.flash_jump(direction, 0.05)
        flash_jumped = True
    press(key, num_press, down_time=0.05, up_time=0.05)
    if direction:
        key_up(direction)
    if flash_jumped:
        utils.sleep_in_floating(0.2)


class ChaosLock(Command):
    """Tp."""

    def __init__(self, pos_changing_threshold=0.1, direction=None, wait_pos_changing_time=3):
        super().__init__(locals())
        self.pos_changing_threshold = float(pos_changing_threshold)
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.wait_pos_changing_time = float(wait_pos_changing_time)

    @staticmethod
    def chaos_lock(pos_changing_threshold, direction, wait_pos_changing_time):
        player_start_pos = config.player_pos

        def player_pos_changed():
            return utils.distance(player_start_pos, config.player_pos) >= pos_changing_threshold

        tries = 0
        arrows = [None, 'left', 'right']
        arrows_len = len(arrows)

        def do_chaos_lock():
            if direction is not None:
                key_down(direction)
                to_released_direction = direction
                utils.sleep_in_floating(0.05)
            else:
                nonlocal tries
                to_released_direction = arrows[tries % arrows_len]
                tries += 1
                key_down(to_released_direction)
                utils.sleep_in_floating(0.05)
            if to_released_direction is not None:
                key_up(to_released_direction)
                utils.sleep_in_floating(0.05)
            press(Key.CHAOS_LOCK, 3, down_time=0.05, up_time=0.05)

        high_level_utils.do_util_matches2(do_chaos_lock, player_pos_changed, max_wait_time=wait_pos_changing_time)

    def main(self):
        ChaosLock.chaos_lock(self.pos_changing_threshold, self.direction, self.wait_pos_changing_time)


class InfernalConcussion(Command):
    """Uses 'InfernalConcussion' once."""

    def __init__(self, direction=None, jump_times=0, walk_time=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)
        self.walk_time = settings.validate_float(walk_time)

    @staticmethod
    def infernal_concussion(direction, jump_times, walk_time, num_press):
        normal_skill(Key.INFERNAL_CONCUSSION, direction, jump_times=jump_times, walk_time=walk_time,
                     num_press=num_press)

    def main(self):
        InfernalConcussion.infernal_concussion(self.direction, self.jump_times, self.walk_time, self.num_press)


class DemonLash(Command):
    """Uses 'DemonLash' once."""

    def __init__(self, direction=None, jump_times=0, num_press=1):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    @staticmethod
    def demon_lash(direction, jump_times, num_press):
        normal_skill(Key.DEMON_LASH, direction, jump_times=jump_times, num_press=num_press)

    def main(self):
        DemonLash.demon_lash(self.direction, self.jump_times, self.num_press)


class Orthrus(Command):
    """Uses 'Orthrus' once."""

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    @staticmethod
    def orthrus(direction, jump_times, num_press):
        normal_skill(Key.ORTHRUS, direction, jump_times=jump_times, num_press=num_press)

    def main(self):
        Orthrus.orthrus(self.direction, self.jump_times, self.num_press)


class DemonCry(Command):
    """Uses 'DemonCry' once."""

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    @staticmethod
    def demon_cry(direction, jump_times, num_press):
        normal_skill(Key.DEMON_CRY, direction, jump_times=jump_times, num_press=num_press)

    def main(self):
        DemonCry.demon_cry(self.direction, self.jump_times, self.num_press)


class BoundlessRage(Command):
    """Uses 'DemonCry' once."""

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    @staticmethod
    def boundless_rage(direction, jump_times, num_press):
        normal_skill(Key.BOUNDLESS_RAGE, direction, jump_times=jump_times, num_press=num_press)

    def main(self):
        BoundlessRage.boundless_rage(self.direction, self.jump_times, self.num_press)


class DemonImpact(Command):
    """Uses 'DemonCry' once."""

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    @staticmethod
    def demon_impact(direction, jump_times, num_press):
        normal_skill(Key.DEMON_IMPACT, direction, jump_times=jump_times, num_press=num_press)

    def main(self):
        DemonImpact.demon_impact(self.direction, self.jump_times, self.num_press)


class DarkMetamorphosis(Command):
    """Uses 'DemonCry' once."""

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    @staticmethod
    def dark_metamorphosis(direction, jump_times, num_press):
        normal_skill(Key.DARK_METAMORPHOSIS, direction, jump_times=jump_times, num_press=num_press)
        utils.sleep_in_floating(1)

    def main(self):
        DarkMetamorphosis.dark_metamorphosis(self.direction, self.jump_times, self.num_press)


class DemonBane(Command):
    """Uses 'DemonCry' once."""

    def __init__(self, direction=None, hold_down_time=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.hold_down_time = float(hold_down_time)

    @staticmethod
    def demon_bane(direction, hold_down_time):
        utils.sleep_in_floating(0.05)
        if direction:
            key_down(direction)
            utils.sleep_in_floating(0.05)
        key_down(Key.DEMON_BANE)
        utils.sleep_in_floating(hold_down_time, 0.1)
        if direction:
            key_up(direction)

    def main(self):
        DemonBane.demon_bane(self.direction)


class CerberusChomp(Command):
    """Uses 'DemonCry' once."""

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    @staticmethod
    def cerberus_chomp(direction, jump_times, num_press):
        normal_skill(Key.CERBERUS_CHOMP, direction, jump_times=jump_times, num_press=num_press)

    def main(self):
        CerberusChomp.cerberus_chomp(self.direction, self.jump_times, self.num_press)


class Nightmare(Command):
    """Uses 'DemonCry' once."""

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    @staticmethod
    def nightmare(direction, jump_times, num_press):
        normal_skill(Key.NIGHTMARE, direction, jump_times=jump_times, num_press=num_press)

    def main(self):
        Nightmare.nightmare(self.direction, self.jump_times, self.num_press)


class SpiritOfRage(Command):
    """Uses 'DemonCry' once."""

    def __init__(self, direction=None, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)

    @staticmethod
    def spirit_of_rage(direction, jump_times, num_press):
        normal_skill(Key.SPIRIT_OF_RAGE, direction, jump_times=jump_times, num_press=num_press)

    def main(self):
        SpiritOfRage.spirit_of_rage(self.direction, 0, self.num_press)


class DemonAwakening(Command):
    """Uses 'DemonCry' once."""

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    @staticmethod
    def demon_awakening(direction, jump_times, num_press):
        normal_skill(Key.DEMON_AWAKENING, direction, jump_times=jump_times, num_press=num_press)

    def main(self):
        DemonAwakening.demon_awakening(self.direction, self.jump_times, self.num_press)


class BlueBlood(Command):
    """Uses 'DemonCry' once."""

    def __init__(self, direction=None, jump_times=0, num_press=3):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction, nullable=True)
        self.num_press = settings.validate_positive_int(num_press)
        self.jump_times = settings.validate_non_negative_int(jump_times)

    @staticmethod
    def blue_blood(direction, jump_times, num_press):
        normal_skill(Key.BLUE_BLOOD, direction, jump_times=jump_times, num_press=num_press)

    def main(self):
        BlueBlood.blue_blood(self.direction, self.jump_times, self.num_press)


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

    @staticmethod
    def sol_janus(direction, jump_times, num_press):
        normal_skill(Key.SOL_JANUS, direction, jump_times=jump_times, num_press=num_press)

    def main(self):
        SolJanus.sol_janus(self.direction, self.jump_times, self.num_press)


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

    @staticmethod
    def erda_shower(direction, jump_times, num_press):
        normal_skill(Key.ERDA_SHOWER, direction, jump_times=jump_times, num_press=num_press)

    def main(self):
        ErdaShower.erda_shower(self.direction, self.jump_times, self.num_press)
