from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_engine.models import AIMessage, AIChatSession
from ai_engine.serializers import (
    AIChatSessionSerializer,
    AIMessageSerializer,
    ChatInputSerializer,
)
from ai_engine.services import (
    build_portfolio_context,
    call_gemini,
    generate_portfolio_analysis,
)

SYSTEM_PROMPT = """You are Zigma, an AI trading assistant for a paper trading platform.
You help users understand their portfolio, explain market concepts, and analyze trading activity.
Provide clear, concise answers. When discussing prices, use the data provided in context.
Do not give personalized financial advice — remind users this is a paper trading simulation."""


class SessionCreateView(CreateAPIView):
    serializer_class = AIChatSessionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SessionListView(ListAPIView):
    serializer_class = AIChatSessionSerializer

    def get_queryset(self):
        return AIChatSession.objects.filter(user=self.request.user).order_by("-updated_at")


class MessageCreateView(APIView):
    def post(self, request, pk):
        try:
            session = AIChatSession.objects.get(pk=pk, user=request.user)
        except AIChatSession.DoesNotExist:
            return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        input_ser = ChatInputSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        user_content = input_ser.validated_data["content"]

        user_msg = AIMessage.objects.create(
            session=session, role="user", content=user_content,
        )

        context = build_portfolio_context(request.user)
        conversation = AIMessage.objects.filter(session=session).order_by("created_at")
        history = "\n".join(f"{m.role}: {m.content}" for m in conversation)

        try:
            ai_reply = call_gemini(SYSTEM_PROMPT, user_content, context + "\n\n--- Chat History ---\n" + history)
        except Exception as e:
            ai_reply = f"I'm sorry, I encountered an error: {e}"

        ai_msg = AIMessage.objects.create(
            session=session, role="assistant", content=ai_reply,
        )

        session.title = user_content[:50]
        session.save(update_fields=["title"])

        return Response(AIMessageSerializer(ai_msg).data, status=status.HTTP_201_CREATED)


class MessageListView(ListAPIView):
    serializer_class = AIMessageSerializer

    def get_queryset(self):
        try:
            session = AIChatSession.objects.get(pk=self.kwargs["pk"], user=self.request.user)
        except AIChatSession.DoesNotExist:
            return AIMessage.objects.none()
        return AIMessage.objects.filter(session=session).order_by("created_at")


class PortfolioAnalyzeView(APIView):
    def post(self, request):
        try:
            analysis = generate_portfolio_analysis(request.user)
        except Exception as e:
            return Response(
                {"error": f"Analysis failed: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"analysis": analysis})
