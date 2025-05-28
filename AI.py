import streamlit as st
from langchain.chains.conversation.base import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
import streamlit.components.v1 as components

# 设置页面配置
st.set_page_config(
    page_title="WideSeek",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 全局样式设置
st.markdown("""
<style>
    .main .block-container {
        max-width: 90%;
        padding-top: 1rem;
    }
    .css-12oz5g7 {
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    .reportview-container {
        background-color: #f5f7fa;
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{'role': 'ai', 'content': '你好主人，我是你的AI助手，我叫小美，很高兴为你服务！'}]
    st.session_state['memory'] = ConversationBufferMemory(return_message=True)
    st.session_state['API_KEY'] = ''
    st.session_state['model_name'] = 'gpt-4o-mini'
    st.session_state['temperature'] = 0.7
    st.session_state['max_tokens'] = 1000


def get_ai_response(user_prompt):
    model = ChatOpenAI(
        model=st.session_state['model_name'],
        temperature=st.session_state['temperature'],
        max_tokens=st.session_state['max_tokens'],
        api_key=st.session_state['API_KEY'],
        base_url='https://twapi.openai-hk.com/v1'
    )
    chain = ConversationChain(llm=model, memory=st.session_state['memory'])
    return chain.invoke({'input': user_prompt})['response']


# 侧边栏内容
with st.sidebar:
    st.markdown("<h2 style='color: #2c3e50;'>小美AI助手设置</h2>", unsafe_allow_html=True)

    # API密钥输入
    api_key = st.text_input(
        'OpenAI API密钥:',
        type='password',
        value=st.session_state['API_KEY'] if 'API_KEY' in st.session_state else '',
        help="请输入您的OpenAI API密钥以使用服务"
    )
    st.session_state['API_KEY'] = api_key

    # 模型选择
    st.subheader("模型设置")
    model_name = st.selectbox(
        '选择AI模型:',
        ('gpt-4o-mini', 'gpt-3.5-turbo', 'gpt-4'),
        index=0,
        help="选择您想要使用的AI模型"
    )
    st.session_state['model_name'] = model_name

    # 参数调整
    st.subheader("生成参数")
    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider(
            '创造性:',
            min_value=0.0,
            max_value=2.0,
            value=st.session_state['temperature'] if 'temperature' in st.session_state else 0.7,
            step=0.1,
            help="控制AI回答的创造性，值越高回答越随机"
        )
    with col2:
        max_tokens = st.slider(
            '最大长度:',
            min_value=100,
            max_value=4000,
            value=st.session_state['max_tokens'] if 'max_tokens' in st.session_state else 1000,
            step=100,
            help="控制AI回答的最大长度"
        )
    st.session_state['temperature'] = temperature
    st.session_state['max_tokens'] = max_tokens

    # 清除对话历史
    if st.button('清除对话历史', key='clear_history'):
        st.session_state['messages'] = [{'role': 'ai', 'content': '你好主人，我是你的AI助手，我叫小美，很高兴为你服务！'}]
        st.session_state['memory'].clear()
        st.experimental_rerun()

    # 帮助信息
    st.markdown("""
    <div style="margin-top: 2rem; padding: 1rem; background-color: #f8f9fa; border-radius: 5px;">
        <h4 style='color: #2c3e50;'>使用说明</h4>
        <ol style='color: #555;'>
            <li>输入您的OpenAI API密钥</li>
            <li>选择您想要使用的AI模型</li>
            <li>调整生成参数（可选）</li>
            <li>在主界面开始与AI对话</li>
        </ol>
        <p style='color: #7f8c8d; font-size: 0.8rem;'>遇到问题？请检查API密钥是否正确</p>
    </div>
    """, unsafe_allow_html=True)

# 主界面
st.markdown("<h1 style='color: #2c3e50;'>🤖 小美AI助手</h1>", unsafe_allow_html=True)

# 显示对话历史
if st.session_state['messages']:
    for message in st.session_state['messages']:
        role, content = message['role'], message['content']
        if role == 'human':
            st.chat_message("user").write(content)
        else:
            st.chat_message("assistant").write(content)

# 用户输入
user_input = st.chat_input("请输入你的问题...")
if user_input:
    if not st.session_state['API_KEY']:
        st.info('请先在侧边栏输入您的OpenAI API密钥！')
        st.stop()

    # 显示用户消息
    st.chat_message("user").write(user_input)
    st.session_state['messages'].append({'role': 'human', 'content': user_input})

    # 获取AI响应
    with st.spinner('小美正在思考，请稍候...'):
        try:
            resp_from_ai = get_ai_response(user_input)
            st.chat_message("assistant").write(resp_from_ai)
            st.session_state['messages'].append({'role': 'ai', 'content': resp_from_ai})
        except Exception as e:
            st.error(f"发生错误: {str(e)}")
            st.session_state['messages'].append({'role': 'ai', 'content': f"抱歉，我遇到了一个错误: {str(e)}"})