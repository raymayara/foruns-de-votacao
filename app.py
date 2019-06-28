import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, HiddenField, StringField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length, ValidationError
#from wtforms.fields.html5 import IntegerField
from wtforms.widgets.html5 import NumberInput
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
#from enum import Enum
# https://devcenter.heroku.com/articles/heroku-postgresql
# https://devcenter.heroku.com/articles/heroku-cli

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'hard to guess string'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app, db)
serie=""

def cadastraAlunos(listaDeNomes, serie):
    for nomes in listaDeNomes.split():
        if nomes not in Alunos.query.all():
            db.session.add(Alunos(aluno=nomes, serie=serie.upper()))
        else:
            flash("Esses alunos já foram cadastrados")
        #db.session.commit()
def validate_serie(form, field):
        if field.data.upper() in str(Sala.query.all()):
            raise ValidationError('Sala já criada')

def validate_serie_votacao(form, field):
        if not(field.data.upper() in str(Sala.query.all())):
            raise ValidationError('Sala não existe')

def validar_senha(form, field):
    if field.data.upper() != str():
        raise ValidationError('Email')

class Votos (FlaskForm):
    quantidade = IntegerField('Quantidade', validators=[DataRequired()], widget=NumberInput(step=1, max=1, min=0))
    quantidade2 = IntegerField('Quantidade', validators=[DataRequired()], widget=NumberInput(step=1, max=1, min=0))
    quantidade3 = IntegerField('Quantidade', validators=[DataRequired()], widget=NumberInput(step=1, max=1, min=0))
    quantidade4 = IntegerField('Quantidade', validators=[DataRequired()], widget=NumberInput(step=1, max=1, min=0))
    quantidade5 = IntegerField('Quantidade', validators=[DataRequired()], widget=NumberInput(step=1, max=1, min=0))

    votacao = HiddenField('ProdutoTipo', validators=[DataRequired()])

    submit = SubmitField('votar')

class Cadastro(FlaskForm):
    serie = StringField('Série', validators=[DataRequired(), validate_serie])
    turma = TextAreaField('Participantes', validators=[DataRequired()])
    submit = SubmitField('Cadastro')

class Criar_votacao(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    serie = StringField('Série', validators=[DataRequired(), validate_serie_votacao])
    opcoes = StringField('Opção 1', validators=[DataRequired()])
    opcoes1 = StringField('Opção 2', validators=[DataRequired()])
    opcoes2 = StringField('Opção 3')
    opcoes3 = StringField('Opção 4')
    opcoes4 = StringField('Opção 5')
    submit5 = SubmitField('Criar')

class Alunos(db.Model):
    __tablename__="Alunos"
    aluno = db.Column(db.String(64), primary_key=True)
    serie = db.Column(db.String(30), db.ForeignKey('Sala.serie'))

class Votacao(db.Model):
    __tablename__="Votacao"

    titulo= db.Column(db.String (30), primary_key=True)
    opcao1= db.Column(db.String (20), default="")
    vot1 = db.Column(db.Integer, default=0)
    opcao2= db.Column(db.String (20), default="")
    vot2 = db.Column(db.Integer, default=0)
    opcao3= db.Column(db.String (20), default="")
    vot3 = db.Column(db.Integer, default=0)
    opcao4= db.Column(db.String (20), default="")
    vot4 = db.Column(db.Integer, default=0)
    opcao5= db.Column(db.String (20), default="")
    vot5= db.Column(db.String (20), default="")

    serie = db.Column(db.String(30), db.ForeignKey('Sala.serie'))

    def __repr__ (self):
        return '<titulo: %r>' % self.titulo

class Sala(db.Model):
    __tablename__="Sala"
    serie= db.Column(db.String (30), primary_key=True, index=True)

    votacoes = db.relationship('Votacao', backref='Sala')
    alunos = db.relationship('Alunos', backref='Sala')

    def __repr__ (self):
        return '<serie: %r' % self.serie

@app.route('/', methods=['GET', 'POST'])
def index():
    form = Cadastro()
    votacao = criarVotacao()
    if form.validate_on_submit():
        db.session.add(Sala(serie=form.serie.data.upper())) #cadastra sala
        cadastraAlunos(form.turma.data, serie=form.serie.data) # cadastra alunos
        db.session.commit()# slava aletrações
        serie=form.serie.data
        return redirect(url_for('criarVotacao'))#, form=votacao

    return render_template('index.html', form=form)

@app.route('/criar-votacao', methods=['GET', 'POST'])
def criarVotacao():
    form = Criar_votacao()

    if form.validate_on_submit():
        if form.titulo.data != None or form.opcoes.data != None or form.opcoes1.data != None or form.opcoes2.data != None or form.opcoes3.data != None or form.opcoes4.data != None:
            db.session.add(Votacao(titulo=form.titulo.data, opcao1=str(form.opcoes.data), opcao2=str(form.opcoes1.data),opcao3=form.opcoes2.data+"", opcao4=form.opcoes3.data,
            opcao5=form.opcoes4.data, serie=form.serie.data.upper()))#Sala.query.filter_by(serie=form.serie.data.upper()).all()[0]
            db.session.commit()
            return redirect(url_for('votacaoCriadas'))
    return render_template('criarVotacao.html', form=form)

@app.route('/votacao-criadas', methods=['GET', 'POST'])
def votacaoCriadas():
    form = Votos()

    '''if form.validate_on_submit:
        votacao = form.votacao.data
        qtd = form.quantidade.data

        return redirect(url_for('votacaoCriadas'))'''
    forms = {}
    votacoes = Votacao.query.all()

    for v in votacoes:
        f = Votos(quantidade=0,votacao=v.titulo,quantidade2=0,quantidade3=0,quantidade4=0,quantidade5=0)
        forms[v] = f

    return render_template('votacaoCriadas.html', votacoes=votacoes, forms=forms)
