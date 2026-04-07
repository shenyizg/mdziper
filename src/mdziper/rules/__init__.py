"""Rule registry for mdziper compression rules."""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set


@dataclass
class Rule:
    name: str
    fn: Callable[[str], str]
    mode: str  # "standard" or "extreme"
    scope: str  # "text", "math", or "global"
    description: str


class RuleRegistry:
    """Central registry for all compression rules."""

    def __init__(self) -> None:
        self._rules: List[Rule] = []

    def register(
        self, name: str, mode: str, scope: str, description: str
    ) -> Callable:
        """Decorator to register a compression rule."""

        def decorator(fn: Callable[[str], str]) -> Callable[[str], str]:
            self._rules.append(Rule(name, fn, mode, scope, description))
            return fn

        return decorator

    def get_rules(
        self,
        mode: str = "standard",
        scope: Optional[str] = None,
        exclude: Optional[Set[str]] = None,
    ) -> List[Rule]:
        """Get rules for the given mode and optional scope.

        mode="standard" returns only standard rules.
        mode="extreme" returns both standard and extreme rules.
        """
        exclude = exclude or set()
        valid_modes = {"standard"} if mode == "standard" else {"standard", "extreme"}
        return [
            r
            for r in self._rules
            if r.mode in valid_modes
            and (scope is None or r.scope == scope)
            and r.name not in exclude
        ]

    def list_rules(self) -> List[Rule]:
        """Return all registered rules."""
        return list(self._rules)


# Global registry instance
registry = RuleRegistry()
