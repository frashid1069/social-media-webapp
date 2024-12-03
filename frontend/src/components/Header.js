

const Header = ({ subtitle }) => {
    const logoPath = `${process.env.PUBLIC_URL}/logo.png`;
    const websiteName = "Aquamarine";


    return (
      <header className="page-header">
        <div className="header-left">
          <img src={logoPath} alt={`${websiteName} logo`} className="header-logo" />
          <span className="website-name">{websiteName}</span>
        </div>
        <h2 className="header-subtitle">{subtitle}</h2>
      </header>
    );
  };
  
  export default Header;