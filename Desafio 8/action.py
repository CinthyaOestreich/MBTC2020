from cgi import parse_multipart, parse_header
from io import BytesIO
from base64 import b64decode
from ibm_watson import SpeechToTextV1, ApiException
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, CategoriesOptions, EntitiesOptions
import json, os
#Action chama action_mbtc
#URL: https://us-south.functions.appdomain.cloud/api/v1/web/cinthyaoestreich%40gmail.com_dev/default/action_mbtc

def main(args):

    # Parse incoming request headers
    _c_type, p_dict = parse_header(
        args['__ow_headers']['content-type']
    )
    
    # Decode body (base64)
    decoded_string = b64decode(args['__ow_body'])

    # Set Headers for multipart_data parsing
    p_dict['boundary'] = bytes(p_dict['boundary'], "utf-8")
    p_dict['CONTENT-LENGTH'] = len(decoded_string)
    
    # Parse incoming request data
    multipart_data = parse_multipart(
        BytesIO(decoded_string), p_dict
    )
   

    try:
        # Build flac file from stream of bytes
        fo = open("audio_sample.flac", 'wb')
        fo.write(multipart_data.get('audio')[0])
        fo.close()
        teste=False
    except: 
        teste=True
    #teste = multipart_data.items
    #Pegando o Carro
    carro=multipart_data.get('car')[0]
    
    if teste == False: 
         
         # Basic Authentication with Watson STT API
        stt_authenticator = BasicAuthenticator(
        'apikey',
        'apikey'
        )

         #Autenticacao STT
        # Construct a Watson STT client with the authentication object
        stt = SpeechToTextV1(authenticator=stt_authenticator)

     # Set the URL endpoint for your Watson STT client
        stt.set_service_url('https://api.us-south.speech-to-text.watson.cloud.ibm.com')

        # Read audio file and call Watson STT API:
        with open(
            os.path.join(
                os.path.dirname(__file__), './.',
                'audio_sample.flac'
            ), 'rb'
        ) as audio_file:
            # Transcribe the audio.flac with Watson STT
            # Recognize method API reference: 
            # https://cloud.ibm.com/apidocs/speech-to-text?code=python#recognize
            stt_result = stt.recognize(
                audio=audio_file,
                content_type='audio/flac',
                model='pt-BR_BroadbandModel'
            ).get_result()

        authenticator_nlu = BasicAuthenticator(
        'apikey',
        'apikey'
        )
        natural_language_understanding = NaturalLanguageUnderstandingV1(version='2020-09-16',authenticator=authenticator_nlu)
        natural_language_understanding.set_service_url('https://api.us-south.natural-language-understanding.watson.cloud.ibm.com')

        texto_stt=stt_result['results'][0]['alternatives'][0]['transcript']
        try:
            nlu_resp = natural_language_understanding.analyze(text=texto_stt,features=Features(entities=EntitiesOptions(sentiment=True, model ='54f2d12a-54fb-4683-b89f-c76c8b93de3f'))).get_result()
        except ApiException as ex:
            print ("Method failed with status code " + str(ex.code) + ": " + ex.message)

    elif teste == True : 
        
        #Pegando o Text 
        texto=multipart_data.get('text')[0]
        carro=multipart_data.get('car')[0]

        authenticator_nlu = BasicAuthenticator(
        'apikey',
        'apikey'
        )
        natural_language_understanding = NaturalLanguageUnderstandingV1(version='2020-09-16',authenticator=authenticator_nlu)
        natural_language_understanding.set_service_url('https://api.us-south.natural-language-understanding.watson.cloud.ibm.com')

        #Definindo features  
        try:
            nlu_resp = natural_language_understanding.analyze(text=texto,features=Features(entities=EntitiesOptions(sentiment=True, model ='54f2d12a-54fb-4683-b89f-c76c8b93de3f'))).get_result()
        except ApiException as ex:
            print ("Method failed with status code " + str(ex.code) + ": " + ex.message)

 
    sent_rec=[]
    sent_json=[]
    score_rec=[]
    score_json=[]
    ent_rec=[]
    ent_json=[]
    ment_json=[]
    #Pegando a lista de sentimentos negativos
    try:
        for x in range(50):
            aux=nlu_resp['entities'][x]['sentiment']['label']
            sent_json.append(nlu_resp['entities'][x]['sentiment']['label'])
            score_json.append(nlu_resp['entities'][x]['sentiment']['score'])
            ent_json.append(nlu_resp['entities'][x]['type'])
            ment_json.append(nlu_resp['entities'][x]['text'])
        
            #print(aux)
            if  aux != 'neutral':
                if aux !='positive':
                    sent_rec.append(nlu_resp['entities'][x]['sentiment']['label'])
                    score_rec.append(nlu_resp['entities'][x]['sentiment']['score'])
                    ent_rec.append(nlu_resp['entities'][x]['type'])
                    #print("entrou")
        
    except:
        saiu=1

    #lista de carros que podemos usar 
    lista= ["FIAT 500","DUCATO","ARGO","FIORINO","MAREA","RENEGADE","CRONOS"]
    lista_seg_op=["TORO","ARGO","DUCATO","FIAT 500","CRONOS","CRONOS","ARGO"]
    lista_prioridade=["SEGURANCA","CONSUMO","DESEMPENHO","MANUTENCAO","CONFORTO","DESIGN","ACESSORIOS"]

    for x in range(len(lista)):
        if carro == lista[x]:
            lista[x]=lista_seg_op[x]

    #Decidindo qual carro escolher 
    if sent_rec !=[]:

        #entidade.append("MANUTENCAO")
        #Sentimento.append(-1)
        #cont=0
        entidade_aux=0
        sent_aux=0

        for x in range(len(score_rec)):
            dif=abs(sent_aux-score_rec[x])

            if dif > 0.1:
                if score_rec[x] < sent_aux:
                    sent_aux= score_rec[x]
                    entidade_aux=ent_rec[x]
                    print(sent_aux,entidade_aux)
            elif dif < 0.1:
            #Desempate
                #print("aqui")
                for y in range(len(lista)):
                    if entidade_aux == lista_prioridade[y]:
                        sent_aux=sent_aux
                        entidade_aux=entidade_aux
                    elif ent_rec[x] == lista_prioridade[y]:
                        sent_aux= score_rec[x]
                        entidade_aux=ent_rec[x]
        
        for x in range(len(lista)):
            if lista_prioridade[x] == entidade_aux:
                sugest=lista[x]
    else:
        sugest=""

    list_json=[]
    for x in range(len(sent_json)):
        list_json.append({"entity":ent_json[x], "sentiment": score_json[x],"mention": ment_json[x]})

    return {
        "recommendation":sugest,
        "entities":list_json
        
        
    }
