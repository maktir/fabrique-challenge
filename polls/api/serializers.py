from rest_framework import serializers
from .models import Poll, Question, Answer, Choice
from django.db.models import Q


class PollSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Poll


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name']
        model = Choice


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Question


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Answer


class QuestionListSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField('get_answers')

    class Meta:
        fields = ['text', 'answers']
        model = Question

    def get_answers(self, question):
        author_id = self.context.get('request').user.id
        answers = Answer.objects.filter(
            Q(question=question) & Q(author__id=author_id))
        serializer = AnswerSerializer(instance=answers, many=True)
        return serializer.data


class UserPollSerializer(serializers.ModelSerializer):
    questions = QuestionListSerializer(read_only=True, many=True)

    class Meta:
        fields = '__all__'
        model = Poll


class AnswerOneTextSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['self_text']
        model = Answer


class UserFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        question_id = self.context.get('request').parser_context['kwargs'][
            'question_pk']
        request = self.context.get('request', None)
        queryset = super(UserFilteredPrimaryKeyRelatedField,
                         self).get_queryset()
        if not request or not queryset:
            return None
        return queryset.filter(question_id=question_id)


class AnswerOneChoiceSerializer(serializers.ModelSerializer):
    one_choice = UserFilteredPrimaryKeyRelatedField(
        many=False,
        queryset=Choice.objects.all()
    )

    class Meta:
        fields = ['one_choice']
        model = Answer


class AnswerMultipleChoiceSerializer(serializers.ModelSerializer):
    many_choice = UserFilteredPrimaryKeyRelatedField(
        many=True,
        queryset=Choice.objects.all()
    )

    class Meta:
        fields = ['many_choice']
        model = Answer
