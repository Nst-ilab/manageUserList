
import boto3
import json
import logging

#Region指定しないと、デフォルトのUSリージョンが使われる
clientLambda = boto3.client('lambda', region_name='ap-northeast-1')

#Log取得
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('Loading function')

def lambda_handler(event, context):

    # 管理しているユーザーリストの一覧を取得する
    list_of_name_list = get_data("ユーザーリストの一覧")
    
    # メッセージとuser_idを取得する
    # メッセージにリスト名が入ってたら動く
    lineText = event["lineMessage"]["events"][0]["message"]["text"]
    user_id = event["lineMessage"]["events"][0]["source"]["userId"]
    target_list = None
    logger.info(lineText)
    for name_list in list_of_name_list:
        if name_list in lineText:
            target_list = name_list
            logger.info("対象リスト: " + target_list)
            break
    if target_list is None:
        return None
    
    # すでにuser_idが登録されているか確認する
    already_exists = "no"
    user_id_list = get_data(target_list)
    logger.info(user_id_list)
    if user_id in user_id_list:
        already_exists = "yes"
    
    # user_idが登録されていなければ登録する
    # user_idが登録されていれば削除する
    logger.info(already_exists)
    if already_exists == "no":
        append_user(target_list,user_id)
        response_message = target_list+"にあなたを登録しました。"
    elif already_exists == "yes":
        remove_user(target_list,user_id)
        response_message = target_list+"からあなたを削除しました。"
    else:
        return None
    return {"message" : response_message}


def append_user(user_list,user_id):
    # listを取得
    user_list_data = get_data(user_list)
    # user_idを追加
    user_list_data.append(user_id)
    # db書き込み
    set_data(user_list,user_list_data)
    return None


def remove_user(user_list,user_id):
    # listを取得
    user_list_data = get_data(user_list)
    # user_idを削除
    user_list_data.remove(user_id)
    # db書き込み
    set_data(user_list,user_list_data)
    return None


def set_data(item,data):
    response = clientLambda.invoke(
        #storageGetサービスを呼び出し
        FunctionName = 'cloud9-storageDao-storageSet-1NAOAUOZ4HX19',
        # RequestResponse = 同期、Event = 非同期 で実行できます
        InvocationType = 'RequestResponse',
        # byte形式でPayloadを作って渡す
        Payload = json.dumps({"key":item, "value": data}).encode("UTF-8")
    )
    logger.info(response)
    return None


def get_data(item):
    payload={}
    response = clientLambda.invoke(
        #storageGetサービスを呼び出し
        FunctionName = 'cloud9-storageDao-storageGet-SV2WOCWTIT0Z',
        # RequestResponse = 同期、Event = 非同期 で実行できます
        InvocationType = 'RequestResponse',
        # byte形式でPayloadを作って渡す
        Payload = json.dumps({"key":item}).encode("UTF-8")
    )
    payload = json.loads(response['Payload'].read().decode())
    logger.info(payload)
    return payload