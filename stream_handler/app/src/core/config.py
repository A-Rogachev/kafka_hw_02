from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """
    Настройки приложения для потоковой обработки данных.
    """

    data_store: str = Field("memory://", alias="DATA_STORE")
    app_name: str = Field("stream_handler", alias="APP_NAME")
    logger_name: str = Field("faust app", alias="LOGGER_NAME")
    broker_address: str = Field(
        "localhost:9092,localhost:9093,localhost:9094", alias="BROKER_ADDRESS"
    )


settings = AppSettings()
