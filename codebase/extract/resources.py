"""
This module contains a collection of methods
used to dynamically allocate the ideal amount
of resources for an extract job.
"""
import math


def calculate_worker_nodes(
    row_count: int, partitions: int, target_nodes: int = 100000
) -> int:
    """
    Calculate the average number of rows per partition.
    Set the minimum number of worker nodes to 2,
    (one for the master node and one for the worker node).

    It calculates the ideal number of worker nodes by
    dividing the average number of rows per partition by
    the target number of rows per worker node and adding
    the minimum number of worker nodes.

    Finally, it rounds up the ideal number of worker nodes
    to the nearest whole number using the math.ceil()
    function from the Python math module.

    :param row_count: Total number of rows to be extracted.
    :param partitions: The provided number of partitions that will be allocated.
    :param target_nodes: Set the target number of rows per worker node.
    :return: Integer value of worker nodes.
    """
    avg_rows_per_partition = row_count / partitions
    min_worker_nodes = 2
    ideal_worker_nodes = min_worker_nodes + (avg_rows_per_partition / target_nodes)
    ideal_worker_nodes = math.ceil(ideal_worker_nodes)
    return ideal_worker_nodes


def convert_memory_to_gb(memory: int, unit: str) -> int:
    """
    Convert the memory value to GB based on the unit.
    :param memory: Memory amount based on provided unit.
    :param unit: Unit identifier to be converted to GB.
    :return: GB value of memory unit.
    """
    if unit == "KB":
        memory_in_gb = memory / 1024**2
    elif unit == "MB":
        memory_in_gb = memory / 1024
    elif unit == "GB":
        memory_in_gb = memory
    elif unit == "TB":
        memory_in_gb = memory * 1024
    else:
        raise ValueError("Invalid memory unit")

    return memory_in_gb


def calculate_partitions_and_worker_nodes(
    row_count: int,
    db_cpu: int,
    db_memory: int,
    target_rows_per_worker_node: int,
    target_rows_per_cpu: int,
    target_rows_per_gb_memory: int,
) -> [int, int]:
    """
    This function uses the following logic to calculate the ideal number of partitions and worker nodes:
    It first sets the target number of rows per worker node.
    It then calculates the average number of rows per CPU by dividing the
    row count by the number of CPUs in the database.
    It calculates the average number of rows per GB of memory by dividing
    the row count by the amount of memory in the database.
    It sets the target number of rows per CPU and the target number of
    rows per GB of memory.
    It calculates the ideal number of partitions by dividing the average number
    of rows per CPU by the target number of rows per CPU.
    It calculates the ideal number of worker nodes by dividing the average
    number of rows per GB of memory by the target
    :param row_count: Total number of rows to be extracted.
    :param db_cpu: The DB CPUs allocated
    :param db_memory: The DB CPUs allocated in GB
    :param target_rows_per_worker_node: Set the target number of rows per worker node.
    :param target_rows_per_cpu: Target number of rows to be allocated to each CPU (vCPU)
    :param target_rows_per_gb_memory: The target number of rows to be allocated to each GB of
    :return: The ideal_partitions and ideal_worker_nodes
    """
    # Calculate the average number of rows per CPU
    avg_rows_per_cpu = row_count / db_cpu

    # Calculate the average number of rows per GB of memory
    avg_rows_per_gb_memory = row_count / db_memory

    # Calculate the ideal number of partitions based on the
    # average number of rows per CPU and the target number of rows per CPU
    ideal_partitions = avg_rows_per_cpu / target_rows_per_cpu

    # Calculate the ideal number of worker nodes based on the
    # average number of rows per GB of memory, the target number
    # of rows per worker node, and the target number of rows per GB of memory
    ideal_worker_nodes = (
        avg_rows_per_gb_memory / target_rows_per_worker_node
    ) / target_rows_per_gb_memory

    # Round up the ideal number of partitions
    # and worker nodes to the nearest whole number
    ideal_partitions = math.ceil(ideal_partitions)
    ideal_worker_nodes = math.ceil(ideal_worker_nodes)

    return ideal_partitions, ideal_worker_nodes
