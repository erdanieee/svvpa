<!DOCTYPE html>
<html lang="en">
	<head>
		<?php require 'meta.php'; ?>
		<!--[if lte IE 8]><script src="js/html5shiv.js"></script><![endif]-->
		<script src="js/jquery.min.js"></script>
		<script src="js/skel.min.js"></script>
		<script src="js/skel-layers.min.js"></script>
		<script src="js/init.js"></script>
		<link rel="stylesheet" href="css/metricsgraphics.css" />
		<noscript>
			<link rel="stylesheet" href="css/skel.css" />
			<link rel="stylesheet" href="css/style.css" />
			<link rel="stylesheet" href="css/style-xlarge.css" />
		</noscript>
	</head>

	<body>
		<?php require 'header.php'; ?>

		<!-- Main -->
		<section id="main" class="wrapper ">
			<div class="container ">
				<header class="major">
					<h2>Vista en directo</h2>
				</header>
				<section>
					<img width="100%" src="<?php echo 'http://'.$_SERVER['HTTP_HOST'].':8081'; ?>" >
				</section>
			</div>
		</section>

		<?php require 'footer.php'; ?>

	</body>
</html>
