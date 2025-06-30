from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


class GptChain:
    template: str = """You are a chatbot having a conversation with a human.
    
    {chat_history}
    Human: {human_input}
    Chatbot:"""
    openai_api_key: str = None
    session_id: str = None
    redis_url: str = None
    redis_password: str = None
    model_name: str = None
    llm_chain = None
    message_history: RedisChatMessageHistory = None

    def __init__(self, openai_api_key, session_id, redis_url, openai_base_url, redis_password=None, model_name="Qwen/Qwen3-32B"):
        self.openai_api_key = openai_api_key
        self.session_id = session_id
        self.redis_url = redis_url
        self.redis_password = redis_password
        self.openai_base_url = openai_base_url
        self.model_name = model_name
        print(f"[DEBUG] GptChain init - API Key exists: {openai_api_key is not None}")
        print(f"[DEBUG] GptChain init - API Key length: {len(openai_api_key) if openai_api_key else 'None'}")
        print(f"[DEBUG] GptChain init - Base URL: {openai_base_url}")
        self.redis_llm_chain_factory()

    def redis_llm_chain_factory(self):
        """
        已经封装外部尽量不要调用此方法
        Returns:
        """
        # 根据是否有密码来构建Redis连接参数
        redis_kwargs = {
            "url": self.redis_url,
            "ttl": 600,
            "session_id": self.session_id
        }
        
        # 如果有Redis密码，添加到连接参数中
        if self.redis_password and self.redis_password.strip():
            # 先检测原本url中是否已经包含密码redis://:<PASSWORD>@<PUBLIC-ENDPOINT>:<PORT>
            if "@" in self.redis_url:
                # 如果包含密码，则不再添加密码
                print("[DEBUG] Redis URL already contains password, not adding again.")
            else:
                # 以redis://:<PASSWORD>@<PUBLIC-ENDPOINT>:<PORT>格式添加密码
                print("[DEBUG] Adding Redis password to connection parameters.")
                url = self.redis_url
                if url.startswith("redis://"):
                    # 如果URL以redis://开头，添加密码
                    redis_kwargs["url"] = f"{url.split('://')[0]}://:{self.redis_password}@{url.split('://')[1]}"
            
        message_history = RedisChatMessageHistory(**redis_kwargs)
        self.message_history = message_history
        memory = ConversationBufferMemory(
            memory_key="chat_history", chat_memory=message_history
        )
        prompt = PromptTemplate(
            input_variables=["chat_history", "human_input"], template=self.template)
        
        print(f"[DEBUG] Before OpenAI init - API Key: {self.openai_api_key[:10]}..." if self.openai_api_key else "[DEBUG] Before OpenAI init - API Key: None")
        print(f"[DEBUG] Before OpenAI init - Base URL: {self.openai_base_url}")
        print(f"[DEBUG] Before OpenAI init - Model Name: {self.model_name}")
        
        try:
            llm = ChatOpenAI(
                model=self.model_name,
                openai_api_key=self.openai_api_key,
                openai_api_base=self.openai_base_url,
                streaming=True,
                callbacks=[StreamingStdOutCallbackHandler()]
            )
            print(f"[DEBUG] ChatOpenAI LLM created successfully with model: {self.model_name}")
        except Exception as e:
            print(f"[DEBUG] ChatOpenAI LLM creation failed: {e}")
            print(f"[DEBUG] Exception type: {type(e)}")
            raise e
            
        # 使用现代的 LCEL (LangChain Expression Language) 替代 LLMChain
        llm_chain = (
            RunnablePassthrough.assign(
                chat_history=lambda x: memory.load_memory_variables({})["chat_history"]
            )
            | prompt
            | llm
            | StrOutputParser()
        )
        self.llm_chain = llm_chain
        self.memory = memory

    def predict(self, question):
        # 使用新的调用方式
        result = self.llm_chain.invoke({"human_input": question})
        
        # 手动保存到内存
        self.memory.save_context(
            {"human_input": question},
            {"output": result}
        )
        
        return result

    def clear_redis(self):
        self.message_history.clear()


if __name__ == "__main__":
    chain = GptChain("your_openai_api_key", "session_id", "redis_url", "openai_base_url", "redis_password")
    song = chain.predict(question="Write me a song about sparkling water.")
    # print(song)
