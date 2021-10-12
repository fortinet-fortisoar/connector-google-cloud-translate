from connectors.core.connector import Connector, ConnectorError, get_logger
from .operations import operations, check_health

logger = get_logger('google-cloud-translate')

class CloudTranslate(Connector):
    def execute(self, config, operation, params, **kwargs):
        action = operations.get(operation)
        logger.info('executing {}'.format(action))
        return action(config, params)

    def check_health(self, config):
        try:
            logger.info('executing check health')
            return check_health(config)
        except Exception as err:
            logger.exception(str(err))
            raise ConnectorError(str(err))



