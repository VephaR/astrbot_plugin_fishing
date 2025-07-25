import functools
import os
from typing import Dict, Any

from quart import (
    Quart, render_template, request, redirect, url_for, session, flash,
    Blueprint, current_app
)


admin_bp = Blueprint(
    "admin_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
)

# 工厂函数现在接收服务实例
def create_app(secret_key: str, services: Dict[str, Any]):
    """
    创建并配置Quart应用实例。

    Args:
        secret_key: 用于session加密的密钥。
        services: 关键字参数，包含所有需要注入的服务实例。
    """
    app = Quart(__name__)
    app.secret_key = os.urandom(24)
    app.config["SECRET_LOGIN_KEY"] = secret_key

    # 将所有注入的服务实例存入app的配置中，供路由函数使用
    # 键名将转换为大写，例如 'user_service' -> 'USER_SERVICE'
    for service_name, service_instance in services.items():
        app.config[service_name.upper()] = service_instance

    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.route("/")
    def root():
        return redirect(url_for("admin_bp.index"))
    return app

def login_required(f):
    @functools.wraps(f)
    async def decorated_function(*args, **kwargs):
        if "logged_in" not in session:
            return redirect(url_for("admin_bp.login"))
        return await f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/login", methods=["GET", "POST"])
async def login():
    if request.method == "POST":
        form = await request.form
        # 从应用配置中获取密钥
        secret_key = current_app.config["SECRET_LOGIN_KEY"]
        if form.get("secret_key") == secret_key:
            session["logged_in"] = True
            await flash("登录成功！", "success")
            return redirect(url_for("admin_bp.index"))
        else:
            await flash("登录失败，请检查密钥！", "danger")
    return await render_template("login.html")

@admin_bp.route("/logout")
async def logout():
    session.pop("logged_in", None)
    await flash("你已成功登出。", "info")
    return redirect(url_for("admin_bp.login"))

@admin_bp.route("/")
@login_required
async def index():
    return await render_template("index.html")

# --- 物品模板管理 (鱼、鱼竿、鱼饵、饰品) ---
# 使用 item_template_service 来处理所有模板相关的CRUD操作

@admin_bp.route("/fish")
@login_required
async def manage_fish():
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    fishes = item_template_service.get_all_fish()
    return await render_template("fish.html", fishes=fishes)

@admin_bp.route("/fish/add", methods=["POST"])
@login_required
async def add_fish():
    form = await request.form
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    # 注意：服务层应处理来自表单的数据转换和验证
    item_template_service.add_fish_template(form.to_dict())
    await flash("鱼类添加成功！", "success")
    return redirect(url_for("admin_bp.manage_fish"))

@admin_bp.route("/fish/edit/<int:fish_id>", methods=["POST"])
@login_required
async def edit_fish(fish_id):
    form = await request.form
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    item_template_service.update_fish_template(fish_id, form.to_dict())
    await flash(f"鱼类ID {fish_id} 更新成功！", "success")
    return redirect(url_for("admin_bp.manage_fish"))

@admin_bp.route("/fish/delete/<int:fish_id>", methods=["POST"])
@login_required
async def delete_fish(fish_id):
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    item_template_service.delete_fish_template(fish_id)
    await flash(f"鱼类ID {fish_id} 已删除！", "warning")
    return redirect(url_for("admin_bp.manage_fish"))

# --- 鱼竿管理 (Rods) ---
@admin_bp.route("/rods")
@login_required
async def manage_rods():
    # 从app配置中获取服务实例
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    # 调用服务层方法获取所有鱼竿模板
    items = item_template_service.get_all_rods()
    return await render_template("rods.html", items=items)


@admin_bp.route("/rods/add", methods=["POST"])
@login_required
async def add_rod():
    form = await request.form
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    # 调用服务层方法添加新的鱼竿模板
    item_template_service.add_rod_template(form.to_dict())
    await flash("鱼竿添加成功！", "success")
    return redirect(url_for("admin_bp.manage_rods"))


@admin_bp.route("/rods/edit/<int:rod_id>", methods=["POST"])
@login_required
async def edit_rod(rod_id):
    form = await request.form
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    # 调用服务层方法更新指定的鱼竿模板
    item_template_service.update_rod_template(rod_id, form.to_dict())
    await flash(f"鱼竿ID {rod_id} 更新成功！", "success")
    return redirect(url_for("admin_bp.manage_rods"))


@admin_bp.route("/rods/delete/<int:rod_id>", methods=["POST"])
@login_required
async def delete_rod(rod_id):
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    # 调用服务层方法删除指定的鱼竿模板
    item_template_service.delete_rod_template(rod_id)
    await flash(f"鱼竿ID {rod_id} 已删除！", "warning")
    return redirect(url_for("admin_bp.manage_rods"))


# --- 鱼饵管理 (Baits) ---
@admin_bp.route("/baits")
@login_required
async def manage_baits():
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    items = item_template_service.get_all_baits()
    return await render_template("baits.html", items=items)


@admin_bp.route("/baits/add", methods=["POST"])
@login_required
async def add_bait():
    form = await request.form
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    item_template_service.add_bait_template(form.to_dict())
    await flash("鱼饵添加成功！", "success")
    return redirect(url_for("admin_bp.manage_baits"))


@admin_bp.route("/baits/edit/<int:bait_id>", methods=["POST"])
@login_required
async def edit_bait(bait_id):
    form = await request.form
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    item_template_service.update_bait_template(bait_id, form.to_dict())
    await flash(f"鱼饵ID {bait_id} 更新成功！", "success")
    return redirect(url_for("admin_bp.manage_baits"))


@admin_bp.route("/baits/delete/<int:bait_id>", methods=["POST"])
@login_required
async def delete_bait(bait_id):
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    item_template_service.delete_bait_template(bait_id)
    await flash(f"鱼饵ID {bait_id} 已删除！", "warning")
    return redirect(url_for("admin_bp.manage_baits"))


# --- 饰品管理 (Accessories) ---
@admin_bp.route("/accessories")
@login_required
async def manage_accessories():
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    items = item_template_service.get_all_accessories()
    return await render_template("accessories.html", items=items)


@admin_bp.route("/accessories/add", methods=["POST"])
@login_required
async def add_accessory():
    form = await request.form
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    item_template_service.add_accessory_template(form.to_dict())
    await flash("饰品添加成功！", "success")
    return redirect(url_for("admin_bp.manage_accessories"))


@admin_bp.route("/accessories/edit/<int:accessory_id>", methods=["POST"])
@login_required
async def edit_accessory(accessory_id):
    form = await request.form
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    item_template_service.update_accessory_template(accessory_id, form.to_dict())
    await flash(f"饰品ID {accessory_id} 更新成功！", "success")
    return redirect(url_for("admin_bp.manage_accessories"))


@admin_bp.route("/accessories/delete/<int:accessory_id>", methods=["POST"])
@login_required
async def delete_accessory(accessory_id):
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    item_template_service.delete_accessory_template(accessory_id)
    await flash(f"饰品ID {accessory_id} 已删除！", "warning")
    return redirect(url_for("admin_bp.manage_accessories"))


# --- 抽卡池管理 ---
@admin_bp.route("/gacha")
@login_required
async def manage_gacha():
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    pools = item_template_service.get_all_gacha_pools()
    return await render_template("gacha.html", pools=pools)


@admin_bp.route("/gacha/add", methods=["POST"])
@login_required
async def add_gacha_pool():
    form = await request.form
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    item_template_service.add_pool_template(form.to_dict())
    await flash("奖池添加成功！", "success")
    return redirect(url_for("admin_bp.manage_gacha"))


@admin_bp.route("/gacha/edit/<int:pool_id>", methods=["POST"])
@login_required
async def edit_gacha_pool(pool_id):
    form = await request.form
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    item_template_service.update_pool_template(pool_id, form.to_dict())
    await flash(f"奖池ID {pool_id} 更新成功！", "success")
    return redirect(url_for("admin_bp.manage_gacha"))


@admin_bp.route("/gacha/delete/<int:pool_id>", methods=["POST"])
@login_required
async def delete_gacha_pool(pool_id):
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    item_template_service.delete_pool_template(pool_id)
    await flash(f"奖池ID {pool_id} 已删除！", "warning")
    return redirect(url_for("admin_bp.manage_gacha"))


# --- 奖池物品详情管理 ---
@admin_bp.route("/gacha/pool/<int:pool_id>")
@login_required
async def manage_gacha_pool_details(pool_id):
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    details = item_template_service.get_pool_details_for_admin(pool_id)

    if not details.get("pool"):
        await flash("找不到指定的奖池！", "danger")
        return redirect(url_for("admin_bp.manage_gacha"))

    enriched_items = []
    for item in details.get("pool").items:
        # 将 dataclass 转换为字典以便修改
        item_dict = item.__dict__
        item_name = "未知物品"
        item_type = item.item_type
        item_id = item.item_id

        # 根据类型从 item_template_service 获取名称
        if item_type == "rod":
            template = item_template_service.item_template_repo.get_rod_by_id(item_id)
            if template:
                item_name = template.name
        elif item_type == "accessory":
            template = item_template_service.item_template_repo.get_accessory_by_id(item_id)
            if template:
                item_name = template.name
        elif item_type == "bait":
            template = item_template_service.item_template_repo.get_bait_by_id(item_id)
            if template:
                item_name = template.name
        elif item_type == "fish":
            template = item_template_service.item_template_repo.get_fish_by_id(item_id)
            if template:
                item_name = template.name
        elif item_type == "titles":
            template = item_template_service.item_template_repo.get_title_by_id(item_id)
            if template:
                item_name = template.name
        elif item_type == "coins":
            item_name = f"{item.quantity} 金币"

        item_dict["item_name"] = item_name  # 添加名称属性
        enriched_items.append(item_dict)

    return await render_template(
        "gacha_pool_details.html",
        pool=details["pool"],
        items=enriched_items,  # 传递丰富化后的物品列表
        all_rods=details["all_rods"],
        all_baits=details["all_baits"],
        all_accessories=details["all_accessories"]
    )


@admin_bp.route("/gacha/pool/<int:pool_id>/add_item", methods=["POST"])
@login_required
async def add_item_to_pool(pool_id):
    form = await request.form
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    item_template_service.add_item_to_pool(pool_id, form.to_dict())
    await flash("成功向奖池中添加物品！", "success")
    return redirect(url_for("admin_bp.manage_gacha_pool_details", pool_id=pool_id))


@admin_bp.route("/gacha/pool/edit_item/<int:item_id>", methods=["POST"])
@login_required
async def edit_pool_item(item_id):
    form = await request.form
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    pool_id = request.args.get("pool_id")
    if not pool_id:
        await flash("编辑失败：缺少奖池ID信息。", "danger")
        return redirect(url_for("admin_bp.manage_gacha"))
    item_template_service.update_pool_item(item_id, form.to_dict())
    await flash(f"奖池物品ID {item_id} 更新成功！", "success")
    return redirect(url_for("admin_bp.manage_gacha_pool_details", pool_id=pool_id))


@admin_bp.route("/gacha/pool/delete_item/<int:item_id>", methods=["POST"])
@login_required
async def delete_pool_item(item_id):
    item_template_service = current_app.config["ITEM_TEMPLATE_SERVICE"]
    pool_id = request.args.get("pool_id")
    if not pool_id:
        await flash("删除失败：缺少奖池ID信息。", "danger")
        return redirect(url_for("admin_bp.manage_gacha"))
    item_template_service.delete_pool_item(item_id)
    await flash(f"奖池物品ID {item_id} 已删除！", "warning")
    return redirect(url_for("admin_bp.manage_gacha_pool_details", pool_id=pool_id))
