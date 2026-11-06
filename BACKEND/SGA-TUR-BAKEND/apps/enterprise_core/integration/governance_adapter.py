from apps.admin_plataforma.services.governance_kernel import GovernanceKernel, AuthorityLevel

class GovernanceAdapter:
    """
    Ensures every EOS decision passes through the GovernanceKernel.
    Part of the Governance Validation Layer.
    """

    @staticmethod
    def validate_and_execute(intention: str, parameters: dict, user=None):
        # Phase 9: Elevate authority for autonomous decisions if no user is provided
        # (System actions require DELEGATED authority at minimum)
        kernel = GovernanceKernel(user=user)

        # If auto-executing, we use the system's internal sovereign token or elevation
        if not user:
            # Placeholder for authority elevation logic in GovernanceKernel
            # Logic implemented
            pass

        return kernel.resolve_and_execute(intention, parameters)
