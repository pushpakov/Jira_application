from marshmallow import Schema, fields, validates, ValidationError


class UserSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    assigned_tasks = fields.List(fields.Nested(lambda: TaskSchema))
    reported_tasks = fields.List(fields.Nested(lambda: TaskSchema))
    comments = fields.List(fields.Nested(lambda: CommentSchema))

    @validates('name')
    def validate_name(self, value):
        if not value:
            raise ValidationError('Name cannot be empty')

    @validates('email')
    def validate_email(self, value):
        if not value:
            raise ValidationError('Email cannot be empty')
        if '@' not in value:
            raise ValidationError('Invalid email format')

    @validates('password')
    def validate_password(self, value):
        if not value:
            raise ValidationError('Password cannot be empty')
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters long')


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)   

    
    @validates('email')
    def validate_email(self, value):
        if not value:
            raise ValidationError('Email cannot be empty')
        if '@' not in value:
            raise ValidationError('Invalid email format')
        
    @validates('password')
    def validate_password(self, value):
        if not value:
            raise ValidationError('Password cannot be empty')
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters long')



class TaskSchema(Schema):
    reporter_email = fields.Str(required=True)
    assignee_email  = fields.Str(required=True)  
    title = fields.Str(required=True) 
    description = fields.Str(required=True)
    reporter = fields.Nested(lambda: UserSchema, exclude=('password',), required=True)
    assignee = fields.Nested(lambda: UserSchema, exclude=('password',), required=True)
    comments = fields.List(fields.Nested(lambda: CommentSchema))

    @validates('title')
    def validate_title(self, value):
        if not value:
            raise ValidationError('Title cannot be empty')

    @validates('description')
    def validate_description(self, value):
        if not value:
            raise ValidationError('Description cannot be empty')




class CommentSchema(Schema):
    task = fields.Nested(lambda: TaskSchema) 
    author = fields.Nested(lambda: UserSchema , exclude=('password',), required=True)
    content = fields.Str(required=True)

    @validates('content')
    def validate_content(self, value):
        if not value:
            raise ValidationError('Content cannot be empty')
