"""add images videos likes comments to news

Revision ID: 236f303247e7
Revises: c46b653bd3d7
Create Date: 2026-04-25 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '236f303247e7'
down_revision = 'c46b653bd3d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем новые поля в таблицу news
    op.add_column('news', sa.Column('summary', sa.String(length=500), nullable=True))
    op.add_column('news', sa.Column('image_url', sa.String(length=500), nullable=True))
    op.add_column('news', sa.Column('video_url', sa.String(length=500), nullable=True))
    op.add_column('news', sa.Column('likes_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Создаём таблицу комментариев
    op.create_table(
        'news_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('news_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.String(length=1000), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['news_id'], ['news.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_news_comments_id', 'news_comments', ['id'])
    op.create_index('ix_news_comments_news_id', 'news_comments', ['news_id'])
    op.create_index('ix_news_comments_user_id', 'news_comments', ['user_id'])
    
    # Создаём таблицу лайков
    op.create_table(
        'news_likes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('news_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['news_id'], ['news.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('news_id', 'user_id', name='unique_news_user_like')
    )
    op.create_index('ix_news_likes_id', 'news_likes', ['id'])
    op.create_index('ix_news_likes_news_id', 'news_likes', ['news_id'])
    op.create_index('ix_news_likes_user_id', 'news_likes', ['user_id'])


def downgrade() -> None:
    # Удаляем таблицы
    op.drop_table('news_likes')
    op.drop_table('news_comments')
    
    # Удаляем добавленные колонки
    op.drop_column('news', 'likes_count')
    op.drop_column('news', 'video_url')
    op.drop_column('news', 'image_url')
    op.drop_column('news', 'summary')
