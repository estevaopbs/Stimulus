import random
from enum import Enum
from typing import Any, Generator


class Order(Enum):
    Random = 0
    Sequential = 1


class IntergroupBehaviour(Enum):
    Select_a_new_group_on_each_show = 0
    Select_a_new_group_on_depletion_of_the_current = 1
    Select_a_new_group_once_all_images_have_been_shown = 2


class SelectionBehaviour(Enum):
    Deterministic = 0
    Probabilistic = 1


class Image:
    def __init__(self, file: str, id: int, rate: int,
                 weight: int | None = None, load: int | None = None) -> None:
        self.file = file
        self.id = id
        self.rate = rate
        self.weight = weight
        self.load = load


class Group:
    def __init__(self, name: str,
                 images: list[dict[str, str | dict[str, str | int | None] | int | None]],
                 id: int, rate: int, weight: int | None = None,
                 load: int | None = None):
        self.name = name
        self.images = [Image(**image) for image in images]
        self.id = id
        self.rate = rate
        self.weight = weight
        self.load = load
        self.last_image = self.images[-1]


class SelectImages:
    def __init__(self, intergroup_show_order: str, intragroup_show_order: str,
                 intergroup_behaviour: str, selection_rate_behaviour: str,
                 screen: Any, allow_image_repeat: bool,
                 amount_of_exhibitions: int, show_time: Any,
                 interval_time: Any, interaction_key: Any, skip_on_click: Any,
                 groups: dict[int, dict[str, str | int |
                                        dict[int, dict[str, str]]]], n: Any) -> None:
        _intergroup_show_order = Order[intergroup_show_order]
        _intragroup_show_order = Order[intragroup_show_order]
        _intergroup_behaviour = IntergroupBehaviour[intergroup_behaviour.replace(
            ' ', '_').replace('\n', '_')]
        _selection_rate_behaviour = SelectionBehaviour[selection_rate_behaviour.replace(
            ' ', '_').replace('\n', '_')]
        _allow_image_repeat = allow_image_repeat
        self.amount_of_exhibitions = amount_of_exhibitions
        groups_ids = [group for group in groups]
        _groups = [groups[group] for group in groups]
        for group, id in zip(_groups, groups_ids):
            group['id'] = id
            images_ids = [image for image in group['images']]
            group['images'] = [group['images'][image]
                               for image in group['images']]
            for image, id_ in zip(group['images'], images_ids):
                image['id'] = id_
        self.groups = [Group(**group) for group in _groups]
        self.last_group = self.groups[-1]
        match _selection_rate_behaviour:
            case SelectionBehaviour.Deterministic:
                groups_load_unity = self.amount_of_exhibitions / \
                    sum([group.rate for group in self.groups])
                for group in self.groups:
                    group.load = group.rate * groups_load_unity
                    group_load_unity = group.load / \
                        sum([image.rate for image in group.images])
                    group.weight = 1
                    for image in group.images:
                        image.load = image.rate * group_load_unity
                        image.weight = 1
                self.reduce = self.reduce_load
                self.valid_images = self.valid_images_deterministic
                self.valid_groups = self.valid_groups_deterministic
            case SelectionBehaviour.Probabilistic:
                for group in self.groups:
                    group.weight = group.rate
                    for image in group.images:
                        image.weight = image.rate
                self.reduce = self.dont_reduce_load
                self.valid_images = self.valid_images_probabilistic
                self.valid_groups = self.valid_groups_probabilistic
            case _:
                raise Exception
        if _allow_image_repeat:
            self.repeating_behaviour = self.repeat
        else:
            self.repeating_behaviour = self.dont_repeat
        match _intergroup_show_order:
            case Order.Random:
                self.next_group = self.random_group
            case Order.Sequential:
                self.next_group = self.sequential_group
            case _:
                raise Exception
        match _intragroup_show_order:
            case Order.Random:
                self.next_image = self.random_image
            case Order.Sequential:
                self.next_image = self.sequential_image
            case _:
                raise Exception
        match _intergroup_behaviour:
            case IntergroupBehaviour.Select_a_new_group_on_each_show:
                self.run = self.select_on_each_show
            case IntergroupBehaviour.Select_a_new_group_on_depletion_of_the_current:
                self.run = self.select_on_depletion_of_the_current
            case IntergroupBehaviour.Select_a_new_group_once_all_images_have_been_shown:
                self.run = self.select_once_all_images_have_been_shown
            case _:
                raise Exception

    @staticmethod
    def dont_repeat(image: Image) -> None:
        image.load = 0
        image.weight = 0

    @staticmethod
    def repeat(image: Image) -> None:
        pass

    @staticmethod
    def valid_images_probabilistic(group) -> list[Image]:
        return [image for image in group.images if image.weight > 0]

    def valid_groups_probabilistic(self) -> list[Group]:
        return [group for group in self.groups if group.weight > 0]

    @staticmethod
    def valid_images_deterministic(group) -> list[Image]:
        return [image for image in group.images if image.load > 0]

    def valid_groups_deterministic(self) -> list[Group]:
        return [group for group in self.groups if group.load > 0]

    @staticmethod
    def reduce_load(item) -> None:
        item.load -= 1

    @staticmethod
    def dont_reduce_load(item) -> None:
        pass

    def random_image(self, group) -> Image:
        images = self.valid_images(group)
        image = random.choices(
            images, weights=[image.weight for image in images])[0]
        self.reduce(image)
        self.repeating_behaviour(image)
        self.reduce(group)
        return image

    def sequential_image(self, group) -> Image:
        images = self.valid_images(group)
        index = None
        if group.last_image in images and images[images.index(group.last_image) + 1:]:
            index = images.index(group.last_image) + 1
        else:
            for image in images:
                if group.images.index(image) > group.images.index(group.last_image):
                    index = images.index(image)
                    break
        if index is None:
            index = 0
        image = images[index]
        group.last_image = image
        self.reduce(image)
        self.repeating_behaviour(image)
        self.reduce(group)
        return image

    def random_group(self) -> Group:
        groups = self.valid_groups()
        group = random.choices(
            groups, weights=[group.weight for group in groups])[0]
        return group

    def sequential_group(self) -> Group:
        groups = self.valid_groups()
        index = None
        if self.last_group in groups and groups[groups.index(self.last_group) + 1:]:
            index = groups.index(self.last_group) + 1
        else:
            for group in groups:
                if self.groups.index(group) > self.groups.index(self.last_group):
                    index = groups.index(group)
                    break
        if index is None:
            index = 0
        group = groups[index]
        self.last_group = group
        return group

    def select_on_each_show(self) -> Generator[Image, None, None]:
        for _ in range(self.amount_of_exhibitions):
            yield self.next_image(self.next_group())

    def select_once_all_images_have_been_shown(self) -> Generator[Image, None, None]:
        group = self.next_group()
        yield self.next_image(group)
        for _ in range(self.amount_of_exhibitions - 1):
            if (group.last_image == group.images[-1] or
                    group.images.index(group.last_image) > group.images.index(self.valid_images(group)[-1])):
                group = self.next_group()
            yield self.next_image(group)

    def select_on_depletion_of_the_current(self) -> Generator[Image, None, None]:
        group = self.next_group()
        for _ in range(self.amount_of_exhibitions):
            if group not in self.valid_groups():
                group = self.next_group()
            yield self.next_image(group)
