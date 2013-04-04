<?xml version="1.0" encoding="big5"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:ms="urn:anything"
>

<xsl:output encoding="big5"/>

<msxsl:script
	xmlns:msxsl="urn:schemas-microsoft-com:xslt"
	language="javascript"
	implements-prefix="ms"
>
</msxsl:script>

<xsl:template match="tei.2">
	<html>
	<head>
		<title><xsl:value-of select="teiheader/filedesc/titlestmt/title"/></title>
	</head>
	<body>
		<xsl:apply-templates select="text/body"/>
	</body>
	</html>
</xsl:template>

<!-- byline 前空四個全形空白 -->
<xsl:template match="byline">
　　　　<xsl:apply-templates/>
</xsl:template>

<!-- 勘誤以紅色顯示 -->
<xsl:template match="corr">
	<font color="red"><xsl:apply-templates/></font>
</xsl:template>

<!-- 卷以綠色顯示 -->
<xsl:template match="juan">
	<xsl:apply-templates/>
</xsl:template>

<xsl:template match="gaiji">
	<xsl:choose>
		<xsl:when test="starts-with(@cb,'SD')"><font face="siddam"><xsl:value-of select="@big5"/></font></xsl:when>
		<!-- 若有 Unicode 則以 Unicode 顯示 -->
		<xsl:when test="@uni!=''"><xsl:text disable-output-escaping="yes">&amp;</xsl:text>#x<xsl:value-of select="@uni"/>;</xsl:when>
		<!-- 若有通用字則以藍色顯示 -->
		<xsl:when test="@nor!=''"><font color="blue"><xsl:value-of select="@nor"/></font></xsl:when>
		<!-- 組字式 -->
		<xsl:when test="@des!=''"><xsl:value-of select="@des"/></xsl:when>
		<xsl:otherwise><xsl:value-of select="@cb"/></xsl:otherwise>
	</xsl:choose>
</xsl:template>

<xsl:template match="gloss">
</xsl:template>

<xsl:template match="head">
	<b><xsl:apply-templates/></b>
</xsl:template>

<xsl:template match="lb">
	<br/><xsl:value-of select="@n"/><xsl:text>║</xsl:text>
</xsl:template>

<xsl:template match="note">
	<xsl:if test="@type='inline'">
		(<xsl:apply-templates/>)
	</xsl:if>
</xsl:template>

<xsl:template match="rdg">
</xsl:template>

<xsl:template match="text()">
	<xsl:value-of select="normalize-space(.)"/>
</xsl:template>

</xsl:stylesheet>