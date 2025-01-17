"""
Консистентное хеширование: мы будем использовать кольцо узлов, где каждый узел имеет свой диапазон значений хэшей.
Данные будут храниться на том узле, чей диапазон включает значение хэша ключа.
Методы управления данными:
    insert: вставка новых данных.
    select: поиск данных по ключу.
    delete: удаление данных по ключу.
    update: обновление данных по ключу.
    resize: изменение количества узлов с последующим перераспределением данных.
"""

import hashlib
from uuid import uuid4


class Node:
    def __init__(self, node_id):
        self.id = node_id
        self.data = {}

    def insert(self, key, value):
        self.data[key] = value

    def select(self, key):
        return self.data.get(key)

    def delete(self, key):
        if key in self.data:
            del self.data[key]

    def update(self, key, new_value):
        if key in self.data:
            self.data[key] = new_value

    def info(self):
        return f'Node {self.id}: {len(self.data)} items'


class Cluster:
    def __init__(self, num_nodes=8):
        # Создаем узлы
        self.nodes = [Node(i + 1) for i in range(num_nodes)]
        # Узлы отсортированы по их идентификаторам
        self.node_map = {i + 1: self.nodes[i] for i in range(len(self.nodes))}
        # Словарь для хранения всех данных по id
        self.data_by_id = {}

    @staticmethod
    def _hash_key(key):
        """Хэшируем ключ."""
        return int(hashlib.md5(str(key).encode()).hexdigest(), 16)

    def _get_node_for_key(self, key_hash):
        """Находим узел для данного ключа."""
        sorted_nodes = sorted(self.node_map.keys())
        node_index = key_hash % len(sorted_nodes)
        return self.node_map[sorted_nodes[node_index]]

    def insert(self, data):
        # Генерируем уникальный ID
        unique_id = str(uuid4())
        key_hash = self._hash_key(unique_id)
        target_node = self._get_node_for_key(key_hash)
        target_node.insert(unique_id, data)
        self.data_by_id[unique_id] = data
        return unique_id

    def select(self, key):
        if key not in self.data_by_id:
            raise KeyError(f'Key {key} does not exist')
        return self.data_by_id[key]

    def delete(self, key):
        if key not in self.data_by_id:
            raise KeyError(f'Key {key} does not exist')
        key_hash = self._hash_key(key)
        target_node = self._get_node_for_key(key_hash)
        target_node.delete(key)
        del self.data_by_id[key]

    def update(self, key, new_data):
        if key not in self.data_by_id:
            raise KeyError(f'Key {key} does not exist')
        key_hash = self._hash_key(key)
        target_node = self._get_node_for_key(key_hash)
        target_node.update(key, new_data)
        self.data_by_id[key] = new_data

    def resize(self, new_num_nodes):
        old_nodes = self.nodes[:]
        self.nodes = [Node(i + 1) for i in range(new_num_nodes)]
        self.node_map = {i + 1: self.nodes[i] for i in range(len(self.nodes))}

        # Перераспределяем все данные по новым узлам
        for key, value in self.data_by_id.items():
            key_hash = self._hash_key(key)
            target_node = self._get_node_for_key(key_hash)
            target_node.insert(key, value)

        # Очищаем старые узлы
        for node in old_nodes:
            node.data.clear()

    def info(self):
        return '\n'.join([node.info() for node in self.nodes])


"""
Класс Node:
    Каждый узел содержит словарь data, где хранятся пары ключ-значение.
    Методы insert, select, delete, update работают непосредственно с этим словарём.
Класс Cluster:
    При инициализации создаются заданное количество узлов.
    Метод _hash_key хэширует ключи данных для равномерного распределения.
    Метод _get_node_for_key находит узел, соответствующий данному ключу, используя остаток от деления хэша на количество узлов.
    Методы insert, select, delete, update управляют данными, находя нужный узел для каждой операции.
    Метод resize изменяет количество узлов и перераспределяет данные.
    Метод info выводит информацию о текущем состоянии каждого узла.
"""


def test_cluster():
    print("Создание кластера...")
    cluster = Cluster(8)

    print("\nВставляем данные...")
    id1 = cluster.insert({'name': 'Нина', 'age': 35})
    id2 = cluster.insert({'name': 'Анна', 'age': 25})
    id3 = cluster.insert({'name': 'Сергей', 'age': 40})

    print("\nПроверяем наличие данных...")
    assert cluster.select(id1) == {'name': 'Нина', 'age': 35}
    assert cluster.select(id2) == {'name': 'Анна', 'age': 25}
    assert cluster.select(id3) == {'name': 'Сергей', 'age': 40}

    print("\nОбновляем данные...")
    cluster.update(id1, {'name': 'Нина', 'age': 31})

    print("\nПроверяем обновленные данные...")
    assert cluster.select(id1) == {'name': 'Нина', 'age': 31}

    print("\nУдаляем данные...")
    cluster.delete(id2)

    try:
        cluster.select(id2)
    except KeyError as e:
        print(f"\nДанные удалены успешно: {e}")

    print("\nИзменяем размер кластера...")
    cluster.resize(12)

    print("\nИнформация о распределении данных:")
    print(cluster.info())


if __name__ == "__main__":
    test_cluster()

