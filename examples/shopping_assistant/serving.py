import time
import sys
import os


sys.path.append("../../src/agents")
from agent import Agent
from sop import SOP, controller


def run(sop: SOP, controller: controller, name="A神", role="user"):
    while True:
        current_node = sop.current_node
        print(current_node.name)
        query = input(f"{name}({role}):")
        current_memory = {"role": "user", "content": f"{name}({role}):{query}"}
        sop.shared_memory["chat_history"].append(current_memory)
        while True:
            next_node, next_role = step(sop, controller)
            flag = next_node.is_interactive
            current_node = next_node
            sop.current_node = current_node

            if next_role == role:
                break
            current_agent = sop.agents[next_role]
            current_agent = sop.agents[next_role]
            response = current_agent.step(
                query, role, name, current_node, sop.temperature
            )
            all = ""
            for res in response:
                all += res
                print(res, end="")
                time.sleep(0.02)
            print()
            sop.shared_memory["chat_history"].append(
                {"role": "assistant", "content": all}
            )

            if flag:
                break
            
            
def step(sop: SOP, controller: controller):
    current_node = sop.current_node
    if len(current_node.next_nodes) == 1:
        next_node = "0"
    else:
        next_node = controller.judge(current_node, sop.shared_memory["chat_history"])
    next_node = current_node.next_nodes[next_node]
    if len(sop.agents.keys()) == 1:
        next_role = list(sop.agents.keys())[0]
    else:
        next_role = controller.allocate_task(
            next_node, sop.shared_memory["chat_history"]
        )
    return next_node, next_role


def autorun(sop: SOP, controller: controller, name="吴家隆", role="AI导购"):
    current_node = sop.current_node
    print(current_node.name)
    current_memory = {"role": "assistant", "content": f"{name}({role}):欢迎来到店铺，请问您有什么需要该买吗"}
    updatememory(current_memory,sop)
    
    while True:
        next_node, next_role = step(sop, controller)
        current_node = next_node
        sop.current_node = current_node
        if next_role == role:
            break
        current_agent = sop.agents[next_role]
        current_agent = sop.agents[next_role]
        response = current_agent.step(
            sop.shared_memory["chat_history"][-1]["content"], role, name, current_node, sop.temperature
        )
        all = f""
        for res in response:
            all += res
            print(res, end="")
            time.sleep(0.02)
        print()
        memory = (
            {"role": "assistant", "content": all}
        )
        updatememory(memory,sop)


def updatememory(memory,sop):
    sop.shared_memory["chat_history"].append(memory)
    for agent in sop.agents.values():
        agent.updatememory(memory)


if __name__ == "__main__":
    shopping_assistant = Agent("AI导购", "吴家隆")
    customer = Agent("客户","A神")
    sop = SOP("muti_shop.json")
    controller = controller(sop.controller_dict)
    
    sop.agents = {"吴家隆": shopping_assistant,"A神":customer}
    shopping_assistant.sop = sop
    
    customer.sop = sop
    autorun(sop, controller)