import yaml
import os


class Config:
    config = None

    @classmethod
    def load_config(cls):
        if cls.config is None:
            with open("configs/config.yaml", "r") as ymlfile:
                cls.config = yaml.safe_load(ymlfile)

    @classmethod
    def get_db_addr(cls):
        return f"{cls.config['DATABASE']['TYPE']}://{cls.config['DATABASE']['USERNAME']}:{cls.config['DATABASE']['PASSWORD']}@{cls.config['DATABASE']['ADDR']}:{cls.config['DATABASE']['PORT']}/{cls.config['DATABASE']['DATABASE']}"

    @classmethod
    def get_token_crypto(cls):
        return cls.config['CRYPTO']

    @classmethod
    def get_wechat_config(cls):
        return cls.config['WECHAT']

    @classmethod
    def get_oss_config(cls):
        return cls.config['OSS']


if os.path.exists("configs/config.yaml"):
    Config.load_config()
else:
    raise FileNotFoundError("config.json not found!")
