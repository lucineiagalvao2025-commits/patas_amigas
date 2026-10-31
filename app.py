import os
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "troque-esta-chave-antes-de-publicar")

# Funciona imediatamente com SQLite. Para MySQL, configure DATABASE_URL conforme o README.
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///patas_amigas.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Tutor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    endereco = db.Column(db.String(250), default="")
    cpf = db.Column(db.String(14), unique=True, nullable=True)
    pets = db.relationship("Pet", backref="tutor", lazy=True)


class Veterinario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    crmv = db.Column(db.String(20), unique=True, nullable=False)
    especialidade = db.Column(db.String(80), default="")
    telefone = db.Column(db.String(20), default="")
    agendamentos = db.relationship("Agendamento", backref="veterinario", lazy=True)


class Servico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    duracao_minutos = db.Column(db.Integer, nullable=False, default=30)
    agendamentos = db.relationship("Agendamento", backref="servico", lazy=True)


class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(40), nullable=False)
    raca = db.Column(db.String(80), default="")
    data_nascimento = db.Column(db.Date, nullable=True)
    peso = db.Column(db.Numeric(7, 2), nullable=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey("tutor.id"), nullable=False)
    agendamentos = db.relationship("Agendamento", backref="pet", lazy=True)


class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey("pet.id"), nullable=False)
    veterinario_id = db.Column(db.Integer, db.ForeignKey("veterinario.id"), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey("servico.id"), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, index=True)
    observacoes = db.Column(db.String(500), default="")
    status = db.Column(db.String(20), nullable=False, default="Agendado")


def parse_decimal(value, field_name):
    try:
        return Decimal(value.replace(",", "."))
    except (InvalidOperation, AttributeError):
        raise ValueError(f"Informe um valor vÃ¡lido para {field_name}.")


@app.route("/")
def index():
    hoje = date.today()
    total_tutores = Tutor.query.count()
    total_pets = Pet.query.count()
    total_vets = Veterinario.query.count()
    total_agendamentos = Agendamento.query.filter(db.func.date(Agendamento.data_hora) == hoje.isoformat()).count()
    proximos = (Agendamento.query.filter(Agendamento.data_hora >= datetime.now(), Agendamento.status != "Cancelado")
                .order_by(Agendamento.data_hora.asc()).limit(6).all())
    return render_template("index.html", total_tutores=total_tutores, total_pets=total_pets,
                           total_vets=total_vets, total_agendamentos=total_agendamentos, proximos=proximos)


@app.route("/tutores", methods=["GET", "POST"])
def tutores():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()
        cpf = request.form.get("cpf", "").strip() or None
        if not nome or not telefone:
            flash("Preencha nome e telefone do tutor.", "error")
        elif cpf and Tutor.query.filter_by(cpf=cpf).first():
            flash("JÃ¡ existe um tutor cadastrado com esse CPF.", "error")
        else:
            db.session.add(Tutor(nome=nome, telefone=telefone,
                                 endereco=request.form.get("endereco", "").strip(), cpf=cpf))
            db.session.commit()
            flash("Tutor cadastrado com sucesso.", "success")
            return redirect(url_for("tutores"))
    q = request.args.get("q", "").strip()
    query = Tutor.query
    if q:
        query = query.filter(or_(Tutor.nome.ilike(f"%{q}%"), Tutor.telefone.ilike(f"%{q}%")))
    return render_template("tutores.html", tutores=query.order_by(Tutor.nome).all(), q=q)


@app.route("/pets", methods=["GET", "POST"])
def pets():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        especie = request.form.get("especie", "").strip()
        tutor_id = request.form.get("tutor_id", type=int)
        if not nome or not especie or not tutor_id or not db.session.get(Tutor, tutor_id):
            flash("Preencha os dados do pet e selecione um tutor vÃ¡lido.", "error")
        else:
            nasc = request.form.get("data_nascimento", "").strip()
            peso_raw = request.form.get("peso", "").strip()
            try:
                data_nasc = date.fromisoformat(nasc) if nasc else None
                peso = parse_decimal(peso_raw, "peso") if peso_raw else None

                if data_nasc and data_nasc > date.today():
                    raise ValueError("A data de nascimento n?o pode ser futura.")

                if peso is not None and peso <= 0:
                    raise ValueError("O peso do pet deve ser maior que zero.")

                db.session.add(Pet(nome=nome, especie=especie, raca=request.form.get("raca", "").strip(),
                                   data_nascimento=data_nasc, peso=peso, tutor_id=tutor_id))
                db.session.commit()
                flash("Pet cadastrado com sucesso.", "success")
                return redirect(url_for("pets"))
            except (ValueError, InvalidOperation) as e:
                flash(str(e) or "Confira a data e o peso informados.", "error")
    q = request.args.get("q", "").strip()
    query = Pet.query.join(Tutor)
    if q:
        query = query.filter(or_(Pet.nome.ilike(f"%{q}%"), Tutor.nome.ilike(f"%{q}%")))
    return render_template("pets.html", pets=query.order_by(Pet.nome).all(),
                           tutores=Tutor.query.order_by(Tutor.nome).all(), q=q)


@app.route("/veterinarios", methods=["GET", "POST"])
def veterinarios():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        crmv = request.form.get("crmv", "").strip()
        if not nome or not crmv:
            flash("Nome e CRMV sÃ£o obrigatÃ³rios.", "error")
        elif Veterinario.query.filter_by(crmv=crmv).first():
            flash("JÃ¡ existe um veterinÃ¡rio com esse CRMV.", "error")
        else:
            db.session.add(Veterinario(nome=nome, crmv=crmv,
                                       especialidade=request.form.get("especialidade", "").strip(),
                                       telefone=request.form.get("telefone", "").strip()))
            db.session.commit()
            flash("VeterinÃ¡rio cadastrado com sucesso.", "success")
            return redirect(url_for("veterinarios"))
    q = request.args.get("q", "").strip()
    query = Veterinario.query
    if q:
        query = query.filter(or_(Veterinario.nome.ilike(f"%{q}%"), Veterinario.crmv.ilike(f"%{q}%")))
    return render_template("veterinarios.html", veterinarios=query.order_by(Veterinario.nome).all(), q=q)


@app.route("/servicos", methods=["GET", "POST"])
def servicos():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        valor_raw = request.form.get("valor", "").strip()
        duracao = request.form.get("duracao_minutos", type=int) or 30
        try:
            valor = parse_decimal(valor_raw, "valor")
            if not nome or valor < 0 or duracao < 5 or duracao > 480:
                raise ValueError("Informe nome, valor nÃ£o negativo e duraÃ§Ã£o entre 5 e 480 minutos.")
            db.session.add(Servico(nome=nome, valor=valor, duracao_minutos=duracao))
            db.session.commit()
            flash("ServiÃ§o cadastrado com sucesso.", "success")
            return redirect(url_for("servicos"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("servicos.html", servicos=Servico.query.order_by(Servico.nome).all())


@app.route("/agendamentos", methods=["GET", "POST"])
def agendamentos():
    if request.method == "POST":
        pet_id = request.form.get("pet_id", type=int)
        vet_id = request.form.get("veterinario_id", type=int)
        servico_id = request.form.get("servico_id", type=int)
        data_raw = request.form.get("data_hora", "").strip()
        try:
            if not data_raw:
                raise ValueError("Informe a data e o horário do agendamento.")

            when = datetime.fromisoformat(data_raw)
            pet = db.session.get(Pet, pet_id)
            vet = db.session.get(Veterinario, vet_id)
            servico = db.session.get(Servico, servico_id)
            if not all([pet, vet, servico]):
                raise ValueError("Selecione um pet, veterinÃ¡rio e serviÃ§o vÃ¡lidos.")
            if when < datetime.now():
                raise ValueError("A data do agendamento deve ser futura.")
            end_new = when.timestamp() + servico.duracao_minutos * 60
            existing = Agendamento.query.filter(
                Agendamento.veterinario_id == vet_id,
                Agendamento.status != "Cancelado"
            ).all()
            for item in existing:
                start_old = item.data_hora.timestamp()
                end_old = start_old + item.servico.duracao_minutos * 60
                if when.timestamp() < end_old and end_new > start_old:
                    raise ValueError("Este veterinÃ¡rio jÃ¡ possui um agendamento nesse horÃ¡rio.")
            ag = Agendamento(pet_id=pet_id, veterinario_id=vet_id, servico_id=servico_id,
                             data_hora=when, observacoes=request.form.get("observacoes", "").strip())
            db.session.add(ag)
            db.session.commit()
            flash("Agendamento criado com sucesso.", "success")
            return redirect(url_for("agendamentos"))
        except ValueError as e:
            flash(str(e), "error")
        except Exception:
            db.session.rollback()
            flash("NÃ£o foi possÃ­vel criar o agendamento. Confira os campos e tente novamente.", "error")
    status = request.args.get("status", "")
    query = Agendamento.query
    if status in ["Agendado", "ConcluÃ­do", "Cancelado"]:
        query = query.filter_by(status=status)
    items = query.order_by(Agendamento.data_hora.desc()).all()
    min_date = datetime.now().strftime("%Y-%m-%dT%H:%M")
    return render_template("agendamentos.html", agendamentos=items, pets=Pet.query.order_by(Pet.nome).all(),
                           veterinarios=Veterinario.query.order_by(Veterinario.nome).all(),
                           servicos=Servico.query.order_by(Servico.nome).all(), min_date=min_date, status=status)


@app.post("/agendamentos/<int:ag_id>/status")
def alterar_status(ag_id):
    ag = db.session.get(Agendamento, ag_id)
    if not ag:
        flash("Agendamento nÃ£o encontrado.", "error")
    else:
        status = request.form.get("status", "")
        if status in ["Agendado", "ConcluÃ­do", "Cancelado"]:
            ag.status = status
            db.session.commit()
            flash("Status atualizado.", "success")
        else:
            flash("Status invÃ¡lido.", "error")
    return redirect(url_for("agendamentos"))


@app.cli.command("init-db")
def init_db():
    """Cria as tabelas da aplicaÃ§Ã£o."""
    with app.app_context():
        db.create_all()
        print("Banco de dados inicializado.")


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")

