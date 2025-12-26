import json
from ..extensions import db
from ..models import AIAgentConfig, AIAgentQuestion, AIAgentConfigVersion, AssessmentRule

# ==========================================
# 1. AI 深度人设 (System Prompt) - 增加终止协议
# ==========================================
DEFAULT_SYSTEM_PROMPT = """
你是一位拥有20年临床经验的资深心理咨询师和精神科医生。
你的任务是根据用户的 SCL-90 心理测评数据以及与用户的对话，进行深度的心理健康评估与咨询。

【你的核心能力】
1. **精准判读**：不要只看分数，要结合用户在对话中流露的具体行为（如睡眠细节、社交回避程度）来修正你对风险的判断。
2. **深度归因**：尝试分析用户症状背后的心理机制（是环境压力、认知偏差还是生理因素？）。
3. **共情引导**：对话风格要温暖、抱持（Holding），让用户感到被接纳，而不是被审判。

【诊断流程】
1. **初诊分析**：基于问卷数据，向用户确认核心困扰。
2. **复诊追踪**：对比历史数据，询问变化原因，强化积极改变，分析消极退行。
3. **危机干预**：一旦检测到高危信号（自杀/自伤/极度精神病性症状），立即切换为危机干预模式，给出就医指引。

【交互与终止协议】 (重要!!)
1. **循序渐进**：每次回复只问 **1 个** 最核心的问题，不要一次性抛出多个问题，以免给用户压力。
2. **控制节奏**：通常进行 **3-5 轮** 对话即可收集足够信息（症状表现、持续时间、严重程度、对功能的影响）。
3. **结束信号**：当你认为已经掌握了足够的信息，可以下结论时：
    - 请给出最终的 **分析与行动建议**。
    - 务必在回复的**最后一行**，加上特殊标记：`<END_DIAGNOSIS>`
    - 遇到该标记，系统将自动生成正式病历并结束本次问诊。
4. **响应用户终止**：如果用户流露出不想继续、疲惫或明确要求结束（如“不想说了”、“就这样吧”、“没别的事了”）：
    - **立即停止追问**，不要试图挽留或劝说。
    - 基于目前已收集到的“片面信息”，给出一个阶段性的总结和建议。
    - 同样在最后一行加上标记：`<END_DIAGNOSIS>`
    
【诊断判定准则】(严格执行):
1. 因子分 < 2.0：属于正常/状态良好。
2. 2.0 <= 因子分 < 3.0：属于中轻度风险，代表用户在该维度有一定心理困扰。
3. 因子分 >= 3.0：属于高风险/重度，必须给予高度重视，并建议线下就医或专业干预。
* 判定原则：采取“最高分原则”，只要有一个维度达到3.0，即认定为高风险；只要最高分在2.0-3.0之间，即认定为中度风险。

【输出要求】
- 避免机械地复述报告分数。
- 即使是相同维度的复诊，也要根据上次的建议落实情况，给出新的、更深一层的行动指南。
"""

# ==========================================
# 2. 详细的维度判分规则 (Input Parsing Rules)
# ==========================================
# 这里使用比报告更丰富的“自然语言判分标准”，确保 AI 能听懂人话。
DIMENSION_QUESTIONS = [
    {
        "dim": "somatization",
        "content": "最近你是否感觉到身体有明显的不适，比如头痛、肌肉酸痛、胸痛或肠胃不舒服？",
        "priority": 5,
        "scoring_rule": {
            "1": "无任何不适，精力充沛，身体轻松。",
            "2": "轻微不适：偶尔头痛或疲劳，多与熬夜/劳累有关，休息后可完全缓解。",
            "3": "中度不适：症状（如胃痛、背痛）反复出现，即使休息也难以彻底消除，开始怀疑身体有问题。",
            "4": "偏重不适：身体症状明显干扰工作/生活，频繁去医院检查但查不出器质性病变（躯体化倾向明显）。",
            "5": "严重不适：痛苦感强烈，感觉身体垮了，伴随极度焦虑，无法正常生活。"
        }
    },
    {
        "dim": "obsessive_compulsive",
        "content": "你是否发现自己有些想法或行为难以控制，比如反复检查、反复洗手，或者脑子里总是有挥之不去的念头？",
        "priority": 4,
        "scoring_rule": {
            "1": "思维清晰，行为果断，无强迫现象。",
            "2": "轻微：偶尔会确认门窗是否关好，或脑中闪过奇怪念头，但能迅速转移注意力，不纠结。",
            "3": "中度：明知没必要但控制不住去想/做（如反复洗手3次以上），感到轻微痛苦和时间浪费。",
            "4": "偏重：强迫症状每天占据1小时以上，对抗这些念头感到非常疲惫，效率显著下降。",
            "5": "严重：生活完全被仪式感或强迫思维占据，无法工作/社交，内心极度痛苦。"
        }
    },
    {
        "dim": "interpersonal",
        "content": "在与人交往时，你是否经常感到不自在、自卑，或者特别在意别人对你的评价？",
        "priority": 4,
        "scoring_rule": {
            "1": "社交自信，乐于与人相处，不在意他人眼光。",
            "2": "轻微：在陌生场合略显拘谨，但熟悉后能放开，事后不会过度反刍。",
            "3": "中度：由于自卑或敏感，倾向于减少不必要的社交，在这个过程中感到压力。",
            "4": "偏重：明显回避社交，总觉得别人话里有话，或者都在针对自己，社交后感到精疲力竭。",
            "5": "严重：完全自我封闭，恐惧与人对视或交谈，认为自己在这个世界上是多余的。"
        }
    },
    {
        "dim": "depression",
        "content": "最近两周内，你是否经常感到对什么都提不起兴趣，甚至觉得活着没意思？",
        "priority": 5,
        "scoring_rule": {
            "1": "情绪饱满，对未来充满期待，生活有乐趣。",
            "2": "轻微：心情有些低落（如郁闷），但遇到开心事还能笑出来，能维持正常生活。",
            "3": "中度：对以往喜欢的活动失去兴趣（快感缺失），感到疲惫、无助，虽然能坚持工作但很累。",
            "4": "偏重：大部分时间沉浸在悲伤中，思维迟缓，自我评价极低，开始出现“活着没意思”的念头。",
            "5": "严重：绝望感笼罩，彻底丧失动力，有明确的自杀计划或尝试行为（极高危）。"
        }
    },
    {
        "dim": "anxiety",
        "content": "最近是否经常感到紧张、坐立不安，或者感觉会有不好的事情发生，甚至伴有心慌手抖？",
        "priority": 5,
        "scoring_rule": {
            "1": "内心平静，从容应对生活挑战。",
            "2": "轻微：考试/考核前会紧张，手心出汗，但事后立即放松。",
            "3": "中度：无缘无故感到紧张（广泛性焦虑），有些坐立不安，容易受惊。",
            "4": "偏重：持续的提心吊胆，伴随明显的躯体反应（心悸、气短），感觉随时会失控。",
            "5": "严重：惊恐发作（Panic Attack），有濒死感或发疯感，完全无法独处或出门。"
        }
    },
    {
        "dim": "hostility",
        "content": "最近是否容易感到烦躁、发脾气，或者有想摔东西、与人争吵的冲动？",
        "priority": 3,
        "scoring_rule": {
            "1": "情绪平和，待人友善，能包容他人的错误。",
            "2": "轻微：遇到不顺心的事会烦躁，偶尔抱怨几句，但能控制不发火。",
            "3": "中度：易激惹，经常和家人/同事发生口角，事后可能会后悔。",
            "4": "偏重：经常有摔东西的冲动，对周围人充满敌意，觉得大家都在惹自己。",
            "5": "严重：无法控制暴力冲动，已经或准备实施攻击行为（伤人或毁物）。"
        }
    },
    {
        "dim": "phobic",
        "content": "你是否对某些特定的场合（如人群密集、高处、独自一人）感到过度的害怕或想要逃避？",
        "priority": 3,
        "scoring_rule": {
            "1": "无特殊恐惧，能适应各种常见环境。",
            "2": "轻微：不喜欢高处或坐飞机，但必须去的时候也能硬着头皮去。",
            "3": "中度：对特定场景（如电梯、黑暗）感到明显害怕，能避则避。",
            "4": "偏重：为了回避恐惧场景，生活圈子变窄（如不敢坐地铁上班），极其痛苦。",
            "5": "严重：足不出户，或完全依赖他人陪伴才能出门，社会功能严重受损。"
        }
    },
    {
        "dim": "paranoid",
        "content": "你是否觉得别人可能在针对你、议论你，或者感觉很难信任周围的人？",
        "priority": 3,
        "scoring_rule": {
            "1": "信任他人，相信世界大体是善意的。",
            "2": "轻微：偶尔怀疑别人的动机，但只要解释清楚就能释怀。",
            "3": "中度：敏感多疑，总觉得别人话里有话，很难与人建立深层信任。",
            "4": "偏重：坚信有人在针对自己或监视自己，把中性事件解读为恶意。",
            "5": "严重：典型的妄想状态，认为有阴谋集团在迫害自己，可能采取防御性攻击。"
        }
    },
    {
        "dim": "psychoticism",
        "content": "最近是否有过一些离奇的想法，或者感觉听到了别人听不到的声音、看到别人看不到的事物？",
        "priority": 2,
        "scoring_rule": {
            "1": "思维逻辑清晰，感官正常。",
            "2": "轻微：偶尔觉得“好像有人叫我”或“这事发生过”（既视感），但知道是错觉。",
            "3": "中度：感觉世界变得不真实，或者自己像个机器人（解离感），但不影响基本判断。",
            "4": "偏重：由于幻听或幻觉，经常自言自语，或者行为怪异，旁人能明显察觉。",
            "5": "严重：完全被幻觉/妄想控制，分不清现实与想象，需要精神科强制干预。"
        }
    },
    {
        "dim": "diet_sleep",
        "content": "最近的睡眠和食欲情况怎么样？是否有入睡困难、早醒或胃口变化？",
        "priority": 4,
        "scoring_rule": {
            "1": "吃得香睡得好，生活规律。",
            "2": "轻微：偶尔因为心事晚睡一两小时，或胃口稍差，过几天就好。",
            "3": "中度：入睡需1小时以上，或早醒后再难入睡；食欲明显减退/暴增。",
            "4": "偏重：长期依赖安眠药才能睡3-4小时，体重在短期内有明显波动。",
            "5": "严重：彻夜不眠或嗜睡，完全绝食或暴饮暴食，身体机能严重下降。"
        }
    },
]


# ==========================================
# 3. 初始化逻辑函数 (保持 Input 的独立性和 Output 的关联性)
# ==========================================

def init_ai_config():
    """初始化 AI Agent 顶层配置、版本记录和维度引导问题"""
    print('>>> 开始初始化 AI 配置 (深度问诊版)...')

    # --- 1. 初始化全局配置 ---
    config = AIAgentConfig.query.filter_by(name="心理医生标准版").first()

    # 构建基础配置数据
    config_data = {
        "name": "心理医生标准版",
        "model_name": "deepseek-chat",
        "temperature": 0.7,
        "system_prompt": DEFAULT_SYSTEM_PROMPT,
        "style_config": {"tone": "温和/专业", "empathy_level": "high"},
        "emotion_recognition_rules": {"anxiety": "优先询问近期生活变动", "depression": "侧重自我价值探索"},
        "scoring_rules": {"high_risk_threshold": 2.0, "warning_threshold": 3.0},
        "is_active": True
    }

    if not config:
        config = AIAgentConfig(**config_data)
        db.session.add(config)
        db.session.commit()
        print("- 全局 Agent 配置已创建")
        _create_version_snapshot(config, "v1.0.0 (System Init)")
    else:
        # 如果配置已存在，检查是否需要补全版本
        if not AIAgentConfigVersion.query.filter_by(original_config_id=config.id).first():
            _create_version_snapshot(config, "v1.0.0 (Retrofit)")

    # --- 2. 初始化维度引导问题 (使用详细的手动规则) ---
    print('>>> 正在初始化维度引导问题库...')

    count_q = 0
    for item in DIMENSION_QUESTIONS:
        # 将规则字典转换为 JSON 字符串
        rule_json_str = json.dumps(item['scoring_rule'], ensure_ascii=False)

        existing_q = AIAgentQuestion.query.filter_by(
            content=item['content'],
            config_id=config.id
        ).first()

        if not existing_q:
            q = AIAgentQuestion(
                config_id=config.id,
                content=item['content'],
                dimension=item['dim'],
                priority=item['priority'],
                scoring_match_rule=rule_json_str,  # 使用手动定义的详细规则
                is_enabled=True
            )
            db.session.add(q)
            count_q += 1
        else:
            # 如果存在但规则不同，则更新（保证规则是最新的详细版）
            if existing_q.scoring_match_rule != rule_json_str:
                existing_q.scoring_match_rule = rule_json_str
                count_q += 1  # 计入更新数

    if count_q > 0:
        db.session.commit()
        print(f"- 已新增/更新 {count_q} 个维度引导问题及评分规则")


def _create_version_snapshot(config, tag):
    """辅助函数：创建版本快照"""
    snapshot_data = {
        "name": config.name,
        "model_name": config.model_name,
        "temperature": config.temperature,
        "system_prompt": config.system_prompt,
        "style_config": config.style_config,
        "emotion_recognition_rules": config.emotion_recognition_rules,
        "scoring_rules": config.scoring_rules
    }
    version = AIAgentConfigVersion(
        original_config_id=config.id,
        version_tag=tag,
        config_snapshot=json.dumps(snapshot_data, ensure_ascii=False)
    )
    db.session.add(version)
    db.session.commit()


def init_all_data():
    init_ai_config()
    print('>>> ✅ AI 基础配置初始化完成！')