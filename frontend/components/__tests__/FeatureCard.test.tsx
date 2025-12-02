import { render, screen } from "@testing-library/react";
import FeatureCard from "../FeatureCard";

describe("FeatureCard", () => {
  const mockProps = {
    title: "AI-Powered Learning",
    description: "Adaptive quizzes that adjust to your skill level",
    icon: "🤖",
  };

  it("renders title correctly", () => {
    render(<FeatureCard {...mockProps} />);
    expect(screen.getByText("AI-Powered Learning")).toBeInTheDocument();
  });

  it("renders description correctly", () => {
    render(<FeatureCard {...mockProps} />);
    expect(
      screen.getByText("Adaptive quizzes that adjust to your skill level"),
    ).toBeInTheDocument();
  });

  it("renders icon correctly", () => {
    render(<FeatureCard {...mockProps} />);
    expect(screen.getByText("🤖")).toBeInTheDocument();
  });

  it("applies terminal aesthetic styling", () => {
    const { container } = render(<FeatureCard {...mockProps} />);
    const card = container.firstChild as HTMLElement;

    expect(card).toHaveClass("border");
    expect(card).toHaveClass("border-terminal-gray");
    expect(card).toHaveClass("bg-terminal-black");
  });

  it("accepts delay prop for animations", () => {
    render(<FeatureCard {...mockProps} delay={0.5} />);
    expect(screen.getByText("AI-Powered Learning")).toBeInTheDocument();
  });

  it("uses default delay when not provided", () => {
    render(<FeatureCard {...mockProps} />);
    expect(screen.getByText("AI-Powered Learning")).toBeInTheDocument();
  });
});
