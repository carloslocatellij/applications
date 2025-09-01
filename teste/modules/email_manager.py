# -*- coding: utf-8 -*-

class EmailManager:
    def __init__(self, db, mail):
        self.db = db
        self.mail = mail
    
    def add_to_queue(self, recipient_email, subject, message, 
                     html_message=None, record_id=None, record_table=None,
                     priority=1):
        """
        Adiciona um e-mail à fila
        """
        try:
            email_id = self.db.email_queue.insert(
                recipient_email=recipient_email,
                subject=subject,
                message=message,
                html_message=html_message,
                record_id=record_id,
                record_table=record_table,
                priority=priority,
                status='pending'
            )
            self.db.commit()
            return email_id, True, "E-mail adicionado à fila com sucesso"
        except Exception as e:
            return None, False, str(e)
    
    def generate_email_from_record(self, template_name, record_id, table_name):
        """
        Gera e-mail baseado em um registro do banco de dados
        """
        try:
            # Busca o template
            template = self.db(self.db.email_templates.name == template_name).select().first()
            if not template:
                return None, False, "Template não encontrado"
            
            # Busca o registro
            table = self.db[table_name]
            record = self.db(table.id == record_id).select().first()
            if not record:
                return None, False, "Registro não encontrado"
            
            # Renderiza o template com os dados do registro
            from gluon.template import render
            context = dict(record=record)
            
            subject = render(template.subject, context=context)
            message = render(template.body_template, context=context)
            html_message = None
            if template.html_template:
                html_message = render(template.html_template, context=context)
            
            # Assume que o registro tem um campo email
            recipient_email = record.email if hasattr(record, 'email') else None
            if not recipient_email:
                return None, False, "E-mail do destinatário não encontrado no registro"
            
            return {
                'recipient_email': recipient_email,
                'subject': subject,
                'message': message,
                'html_message': html_message
            }, True, "E-mail gerado com sucesso"
            
        except Exception as e:
            return None, False, str(e)
    
    def send_from_queue(self, limit=10):
        """
        Processa a fila de e-mails
        """
        sent_count = 0
        failed_count = 0
        
        # Busca e-mails pendentes ordenados por prioridade e data
        pending_emails = self.db(
            (self.db.email_queue.status == 'pending') |
            (self.db.email_queue.status == 'retry')
        ).select(
            orderby=[self.db.email_queue.priority, self.db.email_queue.created_on],
            limitby=(0, limit)
        )
        
        for email_record in pending_emails:
            try:
                # Prepara a mensagem
                message = email_record.message
                if email_record.html_message:
                    message = (email_record.message, email_record.html_message)
                
                # Tenta enviar
                success = self.mail.send(
                    to=email_record.recipient_email,
                    subject=email_record.subject,
                    message=message
                )
                
                if success:
                    # Atualiza como enviado
                    email_record.update_record(
                        status='sent',
                        sent_on=self.db.email_queue.sent_on.default
                    )
                    sent_count += 1
                else:
                    # Incrementa tentativas
                    attempts = email_record.attempts + 1
                    if attempts >= email_record.max_attempts:
                        email_record.update_record(
                            status='failed',
                            attempts=attempts,
                            error_message='Número máximo de tentativas excedido'
                        )
                        failed_count += 1
                    else:
                        email_record.update_record(
                            status='retry',
                            attempts=attempts
                        )
                
            except Exception as e:
                # Marca como falha
                attempts = email_record.attempts + 1
                email_record.update_record(
                    status='failed' if attempts >= email_record.max_attempts else 'retry',
                    attempts=attempts,
                    error_message=str(e)
                )
                failed_count += 1
        
        self.db.commit()
        return sent_count, failed_count
    
    def get_queue_status(self):
        """
        Retorna estatísticas da fila
        """
        pending = self.db(self.db.email_queue.status == 'pending').count()
        sent = self.db(self.db.email_queue.status == 'sent').count()
        failed = self.db(self.db.email_queue.status == 'failed').count()
        retry = self.db(self.db.email_queue.status == 'retry').count()
        
        return {
            'pending': pending,
            'sent': sent,
            'failed': failed,
            'retry': retry,
            'total': pending + sent + failed + retry
        }
