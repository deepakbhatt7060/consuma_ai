import "../App.css";

export const Container = ({ children, style }) => {
  return (
    <div className="container" style={{ ...style }}>
      {children}
    </div>
  );
};
