from __future__ import annotations

import gradio as gr

from people.qa import answer_question, get_examples


def launch() -> None:
    with gr.Blocks(title="PEOPLE｜百家姓名人問答") as demo:
        gr.Markdown(
            "# PEOPLE｜百家姓名人問答\n"
            "輸入姓氏或人物名稱，從資料集即時查找相關人物與生平。"
        )
        question = gr.Textbox(
            label="你的問題",
            placeholder="例如：李姓有哪些人物？或請介紹李白",
            lines=2,
        )
        submit = gr.Button("查詢", variant="primary")
        answer = gr.Markdown(label="回答")
        submit.click(answer_question, inputs=question, outputs=answer)
        question.submit(answer_question, inputs=question, outputs=answer)
        gr.Examples(examples=get_examples(), inputs=question, label="試試看")

    demo.launch()
