from infrastructure_mappings import SDLC_SAGES


class ConfigDataStruct:
    """
    Base Config Data Struct.
    """

    def set_sdlc_stage(self, stage: str):
        """
        Ensure the SDLC stage is valid.
        """
        if stage in SDLC_SAGES:
            return stage
        raise ValueError(
            f"The SDLC stage provided: {stage} is not one of supported {self.SDLC_SAGES}"
        )


class ExtractDataStruct(ConfigDataStruct):
    """
    Config Data Struct for the Extract Pipeline.
    """

    def __init__(
        self,
        version: int,
        source_name: str,
        sdlc_stage: str,
        jdbc_engine: str,
        jdbc_host: str,
        jdbc_port: str,
        vcpu: int,
        memory: dict,
        jdbc_table: str,
        watermark_data_type: str,
        lower_bound: [int, str, float],
        upper_bound: [int, str, float],
        partition_column: str,
        num_partitions: int,
    ):
        self.version = version
        self.source_name = source_name
        self.sdlc_stage = self.set_sdlc_stage(stage=sdlc_stage)
        self.jdbc_engine = jdbc_engine
        self.jdbc_host = jdbc_host
        self.jdbc_port = jdbc_port
        self.vcpu = vcpu
        self.memory = memory
        self.jdbc_table = jdbc_table
        self.watermark_data_type = watermark_data_type
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.partition_column = partition_column
        self.num_partitions = num_partitions
