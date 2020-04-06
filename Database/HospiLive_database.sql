SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
-- --------------------------------------------------------

--
-- Structure de la table `EquipForRea`
--

CREATE TABLE `EquipForRea` (
  `Patient`       char(255)  NOT NULL,
  `EquipmentCode` tinyint(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `EquipFromRea`
--

CREATE TABLE `EquipFromRea` (
  `EquipmentCode` tinyint(4) NOT NULL,
  `Service`       int(11)    NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `PatForRea`
--

CREATE TABLE `PatForRea` (
  `Room`          char(255)  NOT NULL,
  `Service`       int(11)    NOT NULL,
  `ConditionCode` tinyint(4) NOT NULL,
  `HasCovid`      tinyint(1) NOT NULL,
  `O2`            int(11)    NOT NULL,
  `SatO2`         int(11)    NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `Services`
--

CREATE TABLE `Services` (
  `Name`      char(255)  NOT NULL,
  `UF`        int(11)    NOT NULL,
  `Phone`     int(11)    NOT NULL,
  `BackRea`   tinyint(1) NOT NULL,
  `EmptyBeds` int(11)    NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `TransfExt`
--

CREATE TABLE `TransfExt` (
  `Room`    char(255) NOT NULL,
  `Service` int(11)   NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `TransfExtBy`
--

CREATE TABLE `TransfExtBy` (
  `Room`       char(255)  NOT NULL,
  `TransfCode` tinyint(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `TransfExtTo`
--

CREATE TABLE `TransfExtTo` (
  `Room`       char(255)  NOT NULL,
  `TransfCode` tinyint(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `TransfInt`
--

CREATE TABLE `TransfInt` (
  `Room`    char(255) NOT NULL,
  `Service` int(11)   NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `Vectors`
--

CREATE TABLE `Vectors` (
  `Name`   char(255) NOT NULL,
  `Amount` int(11)   NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Index pour les tables exportées
--

--
-- Index pour la table `PatForRea`
--
ALTER TABLE `PatForRea`
  ADD PRIMARY KEY (`Room`);

--
-- Index pour la table `Services`
--
ALTER TABLE `Services`
  ADD PRIMARY KEY (`UF`),
  ADD UNIQUE KEY `Phone` (`Phone`);

--
-- Index pour la table `TransfExt`
--
ALTER TABLE `TransfExt`
  ADD PRIMARY KEY (`Room`);

--
-- Index pour la table `TransfInt`
--
ALTER TABLE `TransfInt`
  ADD PRIMARY KEY (`Room`);

--
-- Index pour la table `Vectors`
--
ALTER TABLE `Vectors`
  ADD PRIMARY KEY (`Name`);