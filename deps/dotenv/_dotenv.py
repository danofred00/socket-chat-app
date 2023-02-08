
#coding:utf-8
import configparser

def env(key :str , file : str = '.env', section :str = 'ENVIRON') -> str:

    config = configparser.ConfigParser()
    config.read(file)
    return config[section][key]
