import random
from enum import Enum


class Order(Enum):
    Random = 0
    Sequential = 1


class IntergroupBehaviour(Enum):
    Select_a_new_group_on_each_show = 0
    Select_a_new_group_on_depletion_of_the_current = 1


class SelectImages:
    def __init__(self, settings: dict):
        self.intergroup_show_order = Order[settings['intergroup_show_order']]
        self.intragroup_show_order = Order[settings['intragroup_show_order']]
        self.intergroup_behaviour = IntergroupBehaviour[settings['intergroup_behaviour'].replace(
            ' ', '_')]
        self.selection_rate_behaviour = settings['selection_rate_behaviour']
        self.screen = settings['screen']
        self.allow_image_repeat = settings['allow_image_repeat']
        self.amount_of_exhibitions = settings['amount_of_exhibitions']
        self.show_time = settings['show_time']
        self.interval_time = settings['interval_time']
        self.test_key = settings['test_key']
        self.skip_on_click = settings['skip_on_click']
        groups_ids = [group for group in settings['groups']]
        self.groups = [settings['groups'][group]
                       for group in settings['groups']]
        for group, id in zip(self.groups, groups_ids):
            group['id'] = id
            images_ids = [image for image in group['images']]
            group['images'] = [group['images'][image]
                               for image in group['images']]
            for image, id_ in zip(group['images'], images_ids):
                image['id'] = id_
            group['last_image'] = group['images'][-1]
        self.last_group = None
        match self.selection_rate_behaviour:
            case 'Deterministic':
                if self.isDeterministicValid():
                    groups_load_unity = self.amount_of_exhibitions / \
                        sum([group['rate'] for group in self.groups])
                    for group in self.groups:
                        group['load'] = group['rate'] * groups_load_unity
                        group_load_unity = group['rate'] / \
                            sum([img['rate'] for img in group['images']])
                        group['weight'] = 1
                        for img in group['images']:
                            img['load'] = img['rate'] * group_load_unity
                            image['weight'] = 1
                    self.reduce = self.reduce_load
                    self.valid_images = self.valid_images_deterministic
                    self.valid_groups = self.valid_groups_deterministic
                else:
                    raise Exception
            case 'Probabilistic':
                for group in self.groups:
                    group['weight'] = group['rate']
                    for image in group['images']:
                        image['weight'] = image['rate']
                self.reduce = self.dont_reduce_load
                self.valid_images = self.valid_images_probabilistic
                self.valid_groups = self.valid_groups_probabilistic
            case _:
                raise Exception
        if not self.allow_image_repeat:
            self.reduce = self.not_repeat
        match self.intergroup_show_order:
            case Order.Random:
                self.next_group = self.random_group
            case Order.Sequential:
                self.next_group = self.sequential_group
            case _:
                raise Exception
        match self.intragroup_show_order:
            case Order.Random:
                self.next_image = self.random_image
            case Order.Sequential:
                self.next_image = self.sequential_image
            case _:
                raise Exception
        match self.intergroup_behaviour:
            case IntergroupBehaviour.Select_a_new_group_on_each_show:
                self.run = self.select_on_each_show
            case IntergroupBehaviour.Select_a_new_group_on_depletion_of_the_current:
                self.run = self.select_on_depletion_of_the_current
            case _:
                raise Exception

    @staticmethod
    def not_repeat(item):
        if 'load' in item:
            item['load'] = 0
        item['weight'] = 0

    @staticmethod
    def valid_images_probabilistic(group: dict) -> list:
        return [image for image in group['images'] if image['weight'] > 0]

    def valid_groups_probabilistic(self) -> list:
        return [group for group in self.groups if group['weight'] > 0]

    @staticmethod
    def valid_images_deterministic(group):
        return [image for image in group['images'] if image['load'] > 0]

    def valid_groups_deterministic(self) -> list:
        return [group for group in self.groups if group['load'] > 0]

    @staticmethod
    def reduce_load(item: dict):
        if 'load' in item:
            item['load'] -= 1

    @staticmethod
    def dont_reduce_load(item: dict):
        pass

    def isDeterministicValid(self) -> bool:
        if self.amount_of_exhibitions % sum([group['rate'] for group in self.groups]) != 0:
            return False
        groups_load_unity = self.amount_of_exhibitions / \
            sum([group['rate'] for group in self.groups])
        for group in self.groups:
            if (group['rate'] * groups_load_unity) % sum([img['rate'] for img in group['images']]) != 0:
                return False
        return True

    def random_image(self, group: dict) -> dict:
        images = self.valid_images(group)
        image = random.choices(
            images, weights=[img['weight'] for img in group['images']])[0]
        self.reduce(image)
        return image

    def sequential_image(self, group: dict) -> dict:
        images = self.valid_images(group)
        for image in group['images'][group['images'].index(group['last_image']) + 1:]:
            if image in images:
                group['last_image'] = image
                self.reduce(image)
                return image
        for image in group['images'][:group['images'].index(group['last_image'])]:
            if image in images:
                group['last_image'] = image
                self.reduce(image)
                return image
        raise Exception

    def random_group(self) -> dict:
        groups = self.valid_groups()
        group = random.choices(
            groups, weights=[group['weight'] for group in groups])[0]
        self.reduce(group)
        return group

    def sequential_group(self) -> dict:
        groups = self.valid_groups()
        for group in groups[groups.index(self.last_group) + 1:]:
            if group in groups:
                self.last_group = group
                self.reduce(group)
                return group
        for group in groups[:groups.index(self.last_group)]:
            if group in groups:
                self.last_group = group
                self.reduce(group)
                return group
        raise Exception

    def select_on_each_show(self):
        for _ in range(self.amount_of_exhibitions):
            yield self.random_image(self.next_group())

    def select_on_depletion_of_the_current(self):
        group = self.next_group()
        for _ in range(self.amount_of_exhibitions):
            if group not in self.valid_groups():
                group = self.next_group()
            yield self.next_image(group)
