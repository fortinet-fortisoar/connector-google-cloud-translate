from google.cloud import translate
from requests import exceptions
from .constants import *
from os.path import join
from connectors.core.connector import ConnectorError, get_logger
from connectors.cyops_utilities.builtins import download_file_from_cyops

logger = get_logger('google-cloud-translate')

class CloudTranslate:

    def __init__(self, config):

        self.project = config.get('project_name', None)
        self.verify = config.get('verify_ssl', True)
        file_path, file_content = self.get_service_acc_data(config)
        self.service_account = file_content
        self.client = translate.TranslationServiceClient.from_service_account_json(file_path)
        self.project_id = self.project if self.project is not None else self.service_account['project_id']


    def get_service_acc_data(self, config):
        try:
            file_meta = config.get('service_account_data')
            logger.info('file metadata= {}'.format(file_meta))
            file_path = join('/tmp', download_file_from_cyops(file_meta.get('@id'))['cyops_file_path'])
            with open(file_path, 'rb') as attachment:
               file_content = attachment.read()
            return file_path, file_content
        except Exception as e:
            error_message = "Error While fetching {0} file data:\n{1}".format(config.get('service_account_data'), str(e))
            logger.exception(error_message)
            raise ConnectorError(error_message)


    def _get_project_id(self):
        return self.project if self.project is not None else self.service_account['project_id']


def get_supported_languages(config, params):
    try:
        cloud_obj_client = CloudTranslate(config)
        # parent = cloud_obj_client.client.location_path(cloud_obj_client.project_id, 'global')
        result = cloud_obj_client.client.get_supported_languages()
        return result
    except Exception as err:
        logger.exception(str(err))
        raise ConnectorError(str(err))


def translate_text(config, params):
    try:
        cloud_obj_client = CloudTranslate(config)
        # parent = cloud_obj_client.client.location_path(cloud_obj_client.project_id, 'global')
        target = language_dict.get(params.get('target'), None)
        source = language_dict.get(params.get('source'), None)
        result = cloud_obj_client.client.translate_text(contents=params.get('input_text'),
                                                        target_language_code=target,
                                                        mime_type= params.get('format') if params.get('format') else None,
                                                        model=params.get('model') if params.get('model') else None,
                                                        source_language_code=source)
        return result
    except Exception as err:
        logger.exception(str(err))
        raise ConnectorError(str(err))


def check_health(config):
    try:
        logger.info('checking connector health')
        res = get_supported_languages(config, {})
        if res:
            return True
    except exceptions.SSLError:
        logger.exception('SSL Certificate Verification Failed')
        raise ConnectorError('SSL Certificate Verification Failed')
    except Exception as err:
        logger.exception(str(err))
        if 'Failed to establish a new connection' in str(err):
            raise ConnectorError('Failed to establish connection/ Invalid URL or Public/Private key')
        raise ConnectorError(str(err))


operations = {
    'translate_text': translate_text,
    'get_supported_languages': get_supported_languages
}
