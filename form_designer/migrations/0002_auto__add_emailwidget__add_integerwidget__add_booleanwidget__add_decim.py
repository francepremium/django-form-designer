# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EmailWidget'
        db.create_table('form_designer_emailwidget', (
            ('widget_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['form_designer.Widget'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('form_designer', ['EmailWidget'])

        # Adding model 'IntegerWidget'
        db.create_table('form_designer_integerwidget', (
            ('widget_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['form_designer.Widget'], unique=True, primary_key=True)),
            ('min_value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('max_value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('form_designer', ['IntegerWidget'])

        # Adding model 'BooleanWidget'
        db.create_table('form_designer_booleanwidget', (
            ('widget_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['form_designer.Widget'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('form_designer', ['BooleanWidget'])

        # Adding model 'DecimalWidget'
        db.create_table('form_designer_decimalwidget', (
            ('widget_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['form_designer.Widget'], unique=True, primary_key=True)),
            ('min_value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('max_value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('max_digits', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('decimal_places', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('form_designer', ['DecimalWidget'])


    def backwards(self, orm):
        # Deleting model 'EmailWidget'
        db.delete_table('form_designer_emailwidget')

        # Deleting model 'IntegerWidget'
        db.delete_table('form_designer_integerwidget')

        # Deleting model 'BooleanWidget'
        db.delete_table('form_designer_booleanwidget')

        # Deleting model 'DecimalWidget'
        db.delete_table('form_designer_decimalwidget')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'form_designer.booleanwidget': {
            'Meta': {'ordering': "('order',)", 'object_name': 'BooleanWidget', '_ormbases': ['form_designer.Widget']},
            'widget_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['form_designer.Widget']", 'unique': 'True', 'primary_key': 'True'})
        },
        'form_designer.choicewidget': {
            'Meta': {'ordering': "('order',)", 'object_name': 'ChoiceWidget', '_ormbases': ['form_designer.Widget']},
            'choices': ('picklefield.fields.PickledObjectField', [], {}),
            'multiple': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'widget_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['form_designer.Widget']", 'unique': 'True', 'primary_key': 'True'})
        },
        'form_designer.decimalwidget': {
            'Meta': {'ordering': "('order',)", 'object_name': 'DecimalWidget', '_ormbases': ['form_designer.Widget']},
            'decimal_places': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_digits': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'widget_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['form_designer.Widget']", 'unique': 'True', 'primary_key': 'True'})
        },
        'form_designer.emailwidget': {
            'Meta': {'ordering': "('order',)", 'object_name': 'EmailWidget', '_ormbases': ['form_designer.Widget']},
            'widget_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['form_designer.Widget']", 'unique': 'True', 'primary_key': 'True'})
        },
        'form_designer.form': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Form'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'form_designer.inputwidget': {
            'Meta': {'ordering': "('order',)", 'object_name': 'InputWidget', '_ormbases': ['form_designer.Widget']},
            'max_length': ('django.db.models.fields.IntegerField', [], {'default': '255'}),
            'widget_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['form_designer.Widget']", 'unique': 'True', 'primary_key': 'True'})
        },
        'form_designer.integerwidget': {
            'Meta': {'ordering': "('order',)", 'object_name': 'IntegerWidget', '_ormbases': ['form_designer.Widget']},
            'max_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'widget_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['form_designer.Widget']", 'unique': 'True', 'primary_key': 'True'})
        },
        'form_designer.tab': {
            'Meta': {'ordering': "('order', 'pk')", 'object_name': 'Tab'},
            'form': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['form_designer.Form']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'form_designer.textareawidget': {
            'Meta': {'ordering': "('order',)", 'object_name': 'TextareaWidget', '_ormbases': ['form_designer.Widget']},
            'widget_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['form_designer.Widget']", 'unique': 'True', 'primary_key': 'True'})
        },
        'form_designer.widget': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Widget'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tab': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['form_designer.Tab']"}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['form_designer']