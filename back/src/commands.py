import click
from flask.cli import with_appcontext
from .extensions import db
# 1. 引入所有模型，确保 db.create_all 能扫描到
# (建议加上 AIConsultation 以便未来扩展，虽然这个脚本目前只操作题目)
from .models import User, Question, QuestionOption, QuestionCategory, AssessmentSession, AssessmentReport, AssessmentRule, AIConsultation
# 2. 引入规则源数据
from .utils.common import SCL90_RULES

# ==========================================
# 1. 准备数据 (完整 SCL-90 数据)
# ==========================================

# 10 个维度
CATEGORIES = [
    "躯体化", "强迫症状", "人际关系敏感", "抑郁", "焦虑",
    "敌对", "恐怖", "偏执", "精神病性", "其他"
]

# 5 个选项
OPTIONS = [
    {"label": "没有", "score": 1},
    {"label": "很轻", "score": 2},
    {"label": "中等", "score": 3},
    {"label": "偏重", "score": 4},
    {"label": "严重", "score": 5},
]

# 90 道题目 (格式: 题目, 维度索引)
SCL90_DATA = [
    ("头痛", 0), ("神经过敏，心中不踏实", 4), ("头脑中有不必要的想法或字句盘旋", 1),
    ("头昏或昏倒", 0), ("对异性的兴趣减退", 3), ("对旁人责备求全", 2),
    ("感到别人能控制您的思想", 8), ("责怪别人制造麻烦", 7), ("忘性大", 1),
    ("担心自己的衣饰整齐及仪态的端正", 1), ("容易烦恼和激动", 5), ("胸痛", 0),
    ("害怕空旷的场所或街道", 6), ("感到自己的精力下降，活动减慢", 3), ("想结束自己的生命", 3),
    ("听到旁人听不到的声音", 8), ("发抖", 4), ("感到大多数人都不可信任", 7),
    ("胃口不好", 9), ("容易哭泣", 3), ("同异性相处时感到害羞不自在", 2),
    ("感到受骗、中了圈套或有人想抓住您", 3), ("无缘无故地突然感到害怕", 4), ("自己不能控制地在发脾气", 5),
    ("怕单独出门", 6), ("经常责怪自己", 3), ("腰痛", 0),
    ("感到难以完成任务", 1), ("感到孤独", 3), ("感到苦闷", 3),
    ("过分担忧", 3), ("对事物不感兴趣", 3), ("感到害怕", 4),
    ("您的感情容易受到伤害", 2), ("旁人能知道你的私下想法", 8), ("感到别人不理解你、不同情你", 2),
    ("感到人们对您不友好，不喜欢您", 2), ("做事必须做得很慢以保证做得正确", 1), ("心跳得很厉害", 4),
    ("恶心或胃部不舒服", 0), ("感到比不上他人", 2), ("肌肉酸痛", 0),
    ("感到有人在监视您、谈论您", 7), ("难以入睡", 9), ("做事必须反复检查", 1),
    ("难以作出决定", 1), ("怕乘电车、公共汽车、地铁或火车", 6), ("呼吸有困难", 0),
    ("一阵阵发冷或发热", 0), ("因为感到害怕而避开某些东西、场合或活动", 6), ("脑子变空了", 1),
    ("身体发麻或刺痛", 0), ("喉咙有梗塞感", 0), ("感到没有前途、没有希望", 3),
    ("不能集中注意", 1), ("感到身体的某一部分软弱无力", 0), ("感到紧张或容易紧张", 4),
    ("感到手或脚发重", 0), ("想到死亡的事", 9), ("吃得太多", 9),
    ("当别人看着您或谈论您时感到不自在", 2), ("有一些不属于你自己的想法", 8), ("有想打人或伤害他人的冲动", 5),
    ("醒得太早", 9), ("必须反复洗手、点数目或触摸某些东西", 1), ("睡得不稳不深", 9),
    ("有想摔坏或破坏东西的冲动", 5), ("有一些别人没有的想法或念头", 7), ("感到对别人神经过敏", 2),
    ("在商店或电影院等人多的地方感到不自在", 6), ("感到任何事情都很困难", 3), ("一阵阵恐惧或惊恐", 4),
    ("感到在公共场合吃东西很不舒服", 2), ("经常与人争论", 5), ("单独一人时神经很紧张", 6),
    ("别人对您的成绩没有作出恰当的评价", 7), ("即使和别人在一起也感到孤单", 8), ("感到坐立不安、心神不定", 4),
    ("感到自己没有什么价值", 3), ("感到熟悉的东西变成陌生或不像是真的", 4), ("大叫或摔东西", 5),
    ("害怕会在公共场合昏倒", 6), ("感到别人想占您的便宜", 7), ("为一些有关性的想法而很苦恼", 8),
    ("您认为应该因为自己的过错而受到惩罚", 8), ("感到要赶快把事情做完", 4), ("感到自己的身体有严重问题", 8),
    ("从未感到和其他人很亲近", 8), ("感到自己有罪", 9), ("感到自己的脑子有毛病", 8)
]


# ==========================================
# 2. 定义命令逻辑
# ==========================================

@click.command('init-data')
@with_appcontext
def seed_scl90_command():
    """【升级版】初始化 SCL-90 题库 + 解释规则"""
    click.echo('>>> 开始初始化 SCL-90 完整数据...')

    # 1. 清理旧数据 (注意顺序，先删子表再删主表)
    click.echo('1. 清理旧数据...')
    try:
        db.session.query(QuestionOption).delete()
        db.session.query(Question).delete()
        db.session.query(QuestionCategory).delete()
        # 清理规则表
        db.session.query(AssessmentRule).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        click.echo(f'⚠️ 清理数据时遇到错误 (可能是表不存在，可忽略): {e}')

    # 2. 写入维度
    click.echo('2. 写入 10 个维度...')
    cat_objs = []
    for name in CATEGORIES:
        cat = QuestionCategory(name=name)
        db.session.add(cat)
        cat_objs.append(cat)
    db.session.commit()

    # 3. 写入题目
    click.echo('3. 写入 90 道题目...')
    for stem, cat_idx in SCL90_DATA:
        # 容错处理
        if 0 <= cat_idx < len(cat_objs):
            category = cat_objs[cat_idx]
        else:
            category = cat_objs[-1]

        q = Question(
            stem=stem,
            type='single_choice',
            difficulty='medium',
            category_id=category.id,
            is_enabled=True
        )
        db.session.add(q)
        db.session.flush()  # 获取 q.id

        # === 核心修复点：使用 enumerate ===
        for idx, opt in enumerate(OPTIONS):
            option = QuestionOption(
                question_id=q.id,
                label=opt['label'],
                score=opt['score'],
                sort_order=idx  # 正确写入排序值 0-4
            )
            db.session.add(option)

    # 4. 写入维度解释规则
    click.echo('4. 写入维度解释规则 (Metadata)...')
    rule_count = 0
    if SCL90_RULES:
        for dim, levels in SCL90_RULES.items():
            for lvl, text in levels.items():
                # text 格式: "轻微：偶尔出现..."
                parts = text.split("：", 1)
                label = parts[0]
                desc = parts[1] if len(parts) > 1 else text

                rule = AssessmentRule(
                    dimension_name=dim,
                    level=lvl,
                    level_label=label,
                    description=desc
                )
                db.session.add(rule)
                rule_count += 1

    db.session.commit()
    click.echo(f'>>> ✅ 成功！导入了 90 道题目和 {rule_count} 条解释规则。')


# ai配置导入
from .utils.init_data import init_all_data
@click.command('init-ai-config')
@with_appcontext
def init_ai_config_command():
    """初始化 AI Agent 配置、维度问题及规则库"""
    # 直接调用分离出去的逻辑
    init_all_data()

