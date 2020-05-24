import yaml


def config_init(filename='./config.yml'):
    """
    Initializace config filu ve kterem ukladame hodnoty promennych
    :param filename: adresa config filu
    :return:
    """
    try:
      cfg = yaml.safe_load(open(filename))
    except IOError:
      msg = f'Loading config file ({filename}) failed.'
      raise IOError(msg)
    return cfg


