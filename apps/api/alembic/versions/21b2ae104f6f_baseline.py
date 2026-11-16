"""baseline

Revision ID: 21b2ae104f6f
Revises:
Create Date: 2026-08-09 16:14:52.297749

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '21b2ae104f6f'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE capabilities (
                id VARCHAR(36) NOT NULL,
                name VARCHAR(100) NOT NULL,
                slug VARCHAR(100) NOT NULL,
                description TEXT,
                category VARCHAR(100) NOT NULL,
                is_active BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                PRIMARY KEY (id),
                UNIQUE (name),
                UNIQUE (slug)
            )
            """
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_capabilities_name ON capabilities (name)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_capabilities_slug ON capabilities (slug)"
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TABLE learner_profiles (
                id VARCHAR(36) NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                display_name VARCHAR(100),
                headline VARCHAR(160),
                bio TEXT,
                location VARCHAR(120),
                profile_image_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                PRIMARY KEY (id),
                UNIQUE (user_id)
            )
            """
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TABLE project_requirements (
                id VARCHAR(36) NOT NULL,
                project_id VARCHAR(36) NOT NULL,
                capability_id VARCHAR(36) NOT NULL,
                description TEXT,
                minimum_proficiency_level INTEGER NOT NULL,
                importance FLOAT NOT NULL,
                required BOOLEAN NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                PRIMARY KEY (id)
            )
            """
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TABLE users (
                id VARCHAR(36) NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(255) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_active BOOLEAN NOT NULL,
                is_verified BOOLEAN NOT NULL,
                is_superuser BOOLEAN NOT NULL,
                role VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                PRIMARY KEY (id),
                UNIQUE (username),
                UNIQUE (email)
            )
            """
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_users_email ON users (email)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_users_username ON users (username)"
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TABLE assessments (
                id VARCHAR(36) NOT NULL,
                capability_id VARCHAR(36) NOT NULL,
                title VARCHAR(150) NOT NULL,
                slug VARCHAR(150) NOT NULL,
                description TEXT,
                difficulty VARCHAR(50) NOT NULL,
                time_limit_minutes INTEGER,
                is_active BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY(capability_id) REFERENCES capabilities (id) ON DELETE CASCADE,
                UNIQUE (slug)
            )
            """
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_assessments_capability_id ON assessments (capability_id)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_assessments_slug ON assessments (slug)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_assessments_difficulty ON assessments (difficulty)"
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TABLE auth_sessions (
                id VARCHAR(36) NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                refresh_token_hash VARCHAR(64) NOT NULL,
                token_family VARCHAR(36) NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                revoked_at TIMESTAMP,
                replaced_by_session_id VARCHAR(36),
                reuse_detected BOOLEAN NOT NULL,
                user_agent VARCHAR(1000),
                ip_address VARCHAR(45),
                device_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                last_used_at TIMESTAMP,
                PRIMARY KEY (id),
                FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE (refresh_token_hash)
            )
            """
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_auth_sessions_user_id ON auth_sessions (user_id)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_auth_sessions_expires_at ON auth_sessions (expires_at)"
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TABLE email_verification_otps (
                id VARCHAR(36) NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                otp_hash VARCHAR(255) NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                attempts INTEGER NOT NULL,
                max_attempts INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                used_at TIMESTAMP,
                PRIMARY KEY (id),
                FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            """
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_email_verification_otps_user_id ON email_verification_otps (user_id)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_email_verification_otps_expires_at ON email_verification_otps (expires_at)"
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TABLE password_reset_tokens (
                id VARCHAR(36) NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                token_hash VARCHAR(64) NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            """
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_password_reset_tokens_user_id ON password_reset_tokens (user_id)"
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TABLE projects (
                id VARCHAR(36) NOT NULL,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                status VARCHAR(30) NOT NULL,
                project_type VARCHAR(50) NOT NULL,
                owner_id VARCHAR(36) NOT NULL,
                organization_id VARCHAR(36),
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE CASCADE
            )
            """
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_projects_owner_id ON projects (owner_id)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_projects_organization_id ON projects (organization_id)"
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TABLE user_capabilities (
                id VARCHAR(36) NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                capability_id VARCHAR(36) NOT NULL,
                proficiency_level INTEGER NOT NULL,
                score FLOAT NOT NULL,
                confidence FLOAT NOT NULL,
                verified BOOLEAN NOT NULL,
                last_assessed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                PRIMARY KEY (id),
                CONSTRAINT uq_user_capability UNIQUE (user_id, capability_id),
                FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY(capability_id) REFERENCES capabilities (id) ON DELETE CASCADE
            )
            """
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_user_capabilities_user_id ON user_capabilities (user_id)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_user_capabilities_capability_id ON user_capabilities (capability_id)"
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TABLE assessment_attempts (
                id VARCHAR(36) NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                assessment_id VARCHAR(36) NOT NULL,
                status VARCHAR(30) NOT NULL,
                question_count INTEGER NOT NULL,
                answered_count INTEGER NOT NULL,
                correct_count INTEGER NOT NULL,
                score FLOAT,
                max_score FLOAT,
                percentage FLOAT,
                started_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                submitted_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY(assessment_id) REFERENCES assessments (id) ON DELETE CASCADE
            )
            """
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_assessment_attempts_user_id ON assessment_attempts (user_id)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_assessment_attempts_assessment_id ON assessment_attempts (assessment_id)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_assessment_attempts_status ON assessment_attempts (status)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_assessment_attempts_user_assessment ON assessment_attempts (user_id, assessment_id)"
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TABLE assessment_questions (
                id VARCHAR(36) NOT NULL,
                assessment_id VARCHAR(36) NOT NULL,
                question_order INTEGER NOT NULL,
                question_type VARCHAR(30) NOT NULL,
                question_text TEXT NOT NULL,
                options_json TEXT,
                correct_answer VARCHAR(500),
                explanation TEXT,
                points INTEGER NOT NULL,
                is_active BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY(assessment_id) REFERENCES assessments (id) ON DELETE CASCADE
            )
            """
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_assessment_questions_assessment_id ON assessment_questions (assessment_id)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_assessment_questions_order ON assessment_questions (assessment_id, question_order)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_assessment_questions_is_active ON assessment_questions (is_active)"
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TABLE assessment_answers (
                id VARCHAR(36) NOT NULL,
                attempt_id VARCHAR(36) NOT NULL,
                question_id VARCHAR(36) NOT NULL,
                selected_answer VARCHAR(500) NOT NULL,
                is_correct BOOLEAN NOT NULL,
                points_earned INTEGER NOT NULL,
                answered_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY(attempt_id) REFERENCES assessment_attempts (id) ON DELETE CASCADE,
                FOREIGN KEY(question_id) REFERENCES assessment_questions (id) ON DELETE CASCADE
            )
            """
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_assessment_answers_attempt_id ON assessment_answers (attempt_id)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_assessment_answers_question_id ON assessment_answers (question_id)"
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TABLE assessment_evidence (
                id VARCHAR(36) NOT NULL,
                attempt_id VARCHAR(36) NOT NULL,
                answer_id VARCHAR(36) NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                capability_id VARCHAR(36) NOT NULL,
                skill_dimension VARCHAR(100),
                evidence_type VARCHAR(50) NOT NULL,
                evidence_score FLOAT NOT NULL,
                evidence_weight FLOAT NOT NULL,
                confidence FLOAT NOT NULL,
                evaluator_type VARCHAR(50) NOT NULL,
                evaluation_reason TEXT,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY(attempt_id) REFERENCES assessment_attempts (id) ON DELETE CASCADE,
                FOREIGN KEY(answer_id) REFERENCES assessment_answers (id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY(capability_id) REFERENCES capabilities (id) ON DELETE CASCADE
            )
            """
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_assessment_evidence_attempt_id ON assessment_evidence (attempt_id)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_assessment_evidence_user_capability ON assessment_evidence (user_id, capability_id)"
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TABLE capability_score_history (
                id VARCHAR(36) NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                capability_id VARCHAR(36) NOT NULL,
                attempt_id VARCHAR(36),
                evidence_id VARCHAR(36),
                score FLOAT NOT NULL,
                proficiency VARCHAR(50),
                confidence FLOAT NOT NULL,
                previous_score FLOAT,
                score_delta FLOAT,
                source VARCHAR(50) NOT NULL,
                reason TEXT,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                PRIMARY KEY (id),
                CONSTRAINT uq_capability_history_attempt UNIQUE (user_id, capability_id, attempt_id),
                FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY(capability_id) REFERENCES capabilities (id) ON DELETE CASCADE,
                FOREIGN KEY(attempt_id) REFERENCES assessment_attempts (id) ON DELETE SET NULL,
                FOREIGN KEY(evidence_id) REFERENCES assessment_evidence (id) ON DELETE SET NULL
            )
            """
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_capability_score_history_user_id ON capability_score_history (user_id)"
        )
    )

    op.execute(
        sa.text(
            "CREATE INDEX ix_capability_score_history_capability_id ON capability_score_history (capability_id)"
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS capability_score_history"))
    op.execute(sa.text("DROP TABLE IF EXISTS assessment_evidence"))
    op.execute(sa.text("DROP TABLE IF EXISTS assessment_answers"))
    op.execute(sa.text("DROP TABLE IF EXISTS assessment_questions"))
    op.execute(sa.text("DROP TABLE IF EXISTS assessment_attempts"))
    op.execute(sa.text("DROP TABLE IF EXISTS user_capabilities"))
    op.execute(sa.text("DROP TABLE IF EXISTS projects"))
    op.execute(sa.text("DROP TABLE IF EXISTS password_reset_tokens"))
    op.execute(sa.text("DROP TABLE IF EXISTS email_verification_otps"))
    op.execute(sa.text("DROP TABLE IF EXISTS auth_sessions"))
    op.execute(sa.text("DROP TABLE IF EXISTS assessments"))
    op.execute(sa.text("DROP TABLE IF EXISTS users"))
    op.execute(sa.text("DROP TABLE IF EXISTS project_requirements"))
    op.execute(sa.text("DROP TABLE IF EXISTS learner_profiles"))
    op.execute(sa.text("DROP TABLE IF EXISTS capabilities"))
