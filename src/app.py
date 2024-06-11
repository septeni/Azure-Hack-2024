# flaskでapiを作成する
# http://sj-dirac:7778/
from flask import Flask, request, jsonify
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
load_dotenv()
#from create_vecterindex import get_embedding, hybrid_search

app = Flask(__name__)

# chatのclientを作成
client = AzureOpenAI(
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-02-01"
)
systemprompt = """あなたは優秀な広告クリエイターです。
Youtube広告で配信する15秒の動画広告を企画します。

入力で与えられた条件や補足情報を基に企画を考えてください。
advertiser_name : 企業名
promotion_name : 商品名
promotion_details : 商品や企業の詳細
kpi : 広告配信する上で重視している指標

出力は下記形式で出力してください。
plan_name : あなたが考える企画を一言で教えてください。
plan_details : その企画の詳細な情報を教えてください。
characters_inad : その企画に登場する人物を教えてください。
scene_description_1 : その企画を実際に動画にする場合、最初のシーンを教えてください。
scene_description_2 ~ scene_description_6 : 2シーン目以降の詳細を教えてください。最大6シーン定義できますがそれより少ないシーン数でも構いません。
scene_prompt_1 : scene_description_1で定義したシーンをDALLE-3で生成するにはどのようなプロンプトを与えますか？入力するプロンプトを"英語で"教えてください。
scene_prompt_2 ~ scene_prompt_6 : 2シーン目以降のプロンプトも"英語で"教えてください。

補足情報
Azure AI Searchを利用して他社の企画や、自社の過去の企画、自社の違う製品の企画を参考に出来ます。
"ただし企業で同じ企画をやることは禁止です。"
Azure AI Searchを使って情報が出てこない場合も企画は考えてください。
"""

q_example = """advertiser_name : septeni     
promotion_name : Odd-AI   
promotion_details : AIで広告のクリエイティブのCTRを事前に予測。要因可視化機能がついている。      
kpi : 認知度の向上
"""
a_example = """plan_name: "未来予測、今を変える"
plan_details : この広告キャンペーンは、AI技術を使って広告クリエイティブのクリックスルーレート(CTR)を事前に予測する「Odd-AI」の機能を強調します。視聴者にAIのパワーを直感的に理解してもらうために、日常生活での瞬間的な選択がどのように最適化されるかを描きます。短い動画で、技術の先進性と使い勝手の良さをアピールし、認知度を高めることを目指します。
characters_inad: 若手マーケティングマネージャー（女性）、AIアナリスト（男性）
scene_description_1 : 若手マーケティングマネージャーがオフィスでデスクワークをしているシーン。彼女が画面に表示された低いCTRの広告に悩んでいる様子を映し出します。
scene_description_2 : 彼女が「Odd-AI」のデモを開始するシーン。コンピュータの画面には「Odd-AI」のロゴが表示され、AIが分析を開始する様子が描かれます。
scene_description_3 : AIアナリストが彼女に「Odd-AI」の特徴と利点を説明するシーン。画面にはCTR予測と要因の可視化が映し出されます。
scene_description_4 : 実際にCTRが改善された広告のビフォーアフターを比較するシーン。新しいCTRの高い広告がディスプレイされます。
scene_description_5 : マーケティングマネージャーが明るい表情で同僚に結果を報告するシーン。オフィスの背景で、チームが彼女の成功を祝います。
scene_description_6 : 最終シーンで「Odd-AI」のロゴとともに「未来予測、今を変える」というスローガンが表示されます。製品の信頼性と効果を印象づける強力なメッセージで締めくくります。
scene_prompt_1 : "Young female marketing manager at her office desk, looking worried while analyzing a digital ad with low CTR on her computer screen."
scene_prompt_2 : "Startup of the 'Odd-AI' demo on a computer screen showing the Odd-AI logo and AI beginning its analysis in a modern office setting."
scene_prompt_3 : "AI analyst explaining the features and benefits of 'Odd-AI' to a young female manager, with CTR predictions and factor visualizations displayed on a screen."
scene_prompt_4 : "Before and after comparison of a digital advertisement showing improvement in CTR, with the new ad displayed prominently."
scene_prompt_5 : "Young female marketing manager happily reporting improved ad results to her colleagues in a lively office environment."
scene_prompt_6 : "Final scene with the 'Odd-AI' logo and the slogan 'Predict the future, change the now' displayed on the screen, emphasizing the product's reliability and effectiveness."
"""
few_shot_messages = []
few_shot_messages.append({
    "role": "user",
    "content": q_example
})
few_shot_messages.append({
    "role": "assistant",
    "content": a_example
})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()

    if 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    user_message = data['message']
    response = client.chat.completions.create(model="gpt-4",
                                        messages=few_shot_messages + [
                                            {"role": "system", "content": systemprompt},
                                            {"role": "user", "content": user_message}],
                                        temperature=1.0,
                                        max_tokens=2048)
    chat_response = response.choices[0].message.content

    return chat_response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7778)
    # ローカル環境でpython ./src/app.pyを立ち上げて下記を投げると返ってくる
    # curl -X POST http://sj-dirac:7778/chat -H "Content-Type: application/json" -d '{"message": "advertiser_name : Microsoft Corporation promotion_name : Azure promotion_details : クラウドコンピューティングプラットフォームおよびサービス、生成AIをOfficeとの連携することで業務効率化を目指している。 kpi : 認知度の向上"}'