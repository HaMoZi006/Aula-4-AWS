import boto3
import json
import os
from datetime import datetime

s3     = boto3.client('s3')
BUCKET = os.environ.get('BUCKET_NAME', 'SEU-BUCKET-AQUI')


def lambda_handler(event, context):
    # Function URL envia o body como string — precisa fazer parse
    body = event.get('body', '{}')
    if isinstance(body, str):
        body = json.loads(body or '{}')

    filename     = body.get('filename', '').strip()
    content_type = body.get('contentType', 'application/octet-stream')

    if not filename:
        return resposta(400, {'error': 'Campo "filename" é obrigatório'})

    # Timestamp no nome evita sobrescrever arquivos com o mesmo nome
    ts  = datetime.now().strftime('%Y%m%d%H%M%S%f')
    key = f"uploads/{ts}-{filename}"

    # A Lambda usa as credenciais da role automaticamente — sem chave no código!
    # generate_presigned_url assina a URL usando as permissões da role (s3:PutObject)
    # O browser vai usar essa URL pra fazer o PUT direto no S3, sem passar pela Lambda
    presigned_url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket':      BUCKET,
            'Key':         key,
            'ContentType': content_type,
        },
        ExpiresIn=300  # URL válida por 5 minutos
    )

    print(f"Presigned URL gerada para: {key}")  # aparece no CloudWatch

    return resposta(200, {
        'uploadUrl': presigned_url,
        'fileKey':   key,
        'publicUrl': f"https://{BUCKET}.s3.amazonaws.com/{key}",
    })


def resposta(status, body):
    return {
        'statusCode': status,
        'headers': {
            'Content-Type':                 'application/json',
        },
        'body': json.dumps(body),
    }
